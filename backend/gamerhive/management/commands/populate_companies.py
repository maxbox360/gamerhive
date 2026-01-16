from django.core.management.base import BaseCommand
from igdb.wrapper import IGDBWrapper
import os
import json
from time import sleep

from gamerhive.models import Game, Company

CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")


class Command(BaseCommand):
    help = "Populate Company model from IGDB based on existing games (optimized)"

    BATCH_SIZE = 500  # IGDB allows up to 500 per request

    def handle(self, *args, **options):
        self.stdout.write("Connecting to IGDB...")
        self.igdb = IGDBWrapper(CLIENT_ID, ACCESS_TOKEN)

        self.stdout.write("Fetching all game IDs...")
        game_ids = list(Game.objects.exclude(igdb_game_id__isnull=True)
                        .values_list("igdb_game_id", flat=True))
        total_games = len(game_ids)
        self.stdout.write(f"Found {total_games} games to process.")

        self.stdout.write("Collecting unique company IDs from games in batches...")
        company_ids = self.collect_company_ids(game_ids)
        self.stdout.write(self.style.NOTICE(f"Found {len(company_ids)} unique companies to fetch."))

        self.populate_companies(company_ids)
        self.stdout.write(self.style.SUCCESS("Finished populating company data!"))

    # -------------------------
    # Core logic
    # -------------------------

    def collect_company_ids(self, game_ids):
        """
        Fetch involved_companies for all games in batches to reduce API calls.
        Returns a set of unique company IDs.
        """
        company_ids = set()
        total_games = len(game_ids)

        for batch_start in range(0, total_games, self.BATCH_SIZE):
            batch = game_ids[batch_start:batch_start + self.BATCH_SIZE]
            query = f"fields game, company; where game = ({', '.join(map(str, batch))}); limit {self.BATCH_SIZE};"
            response = self.igdb.api_request("involved_companies", query)
            data = self._decode_response(response)

            for ic in data:
                company_ids.add(ic["company"])

            self.stdout.write(f"Processed games {batch_start + 1}-{batch_start + len(batch)} / {total_games}")

            # optional: gentle sleep to avoid hitting rate limits
            sleep(0.1)

        return company_ids

    def populate_companies(self, company_ids):
        """
        Fetch company details from IGDB in batches and save them to DB.
        Skips companies that already exist.
        """
        existing_ids = set(Company.objects.values_list("igdb_company_id", flat=True))
        new_company_ids = [c for c in company_ids if c not in existing_ids]

        total_companies = len(new_company_ids)
        self.stdout.write(f"Fetching and saving {total_companies} new companies...")

        for batch_start in range(0, total_companies, self.BATCH_SIZE):
            batch = new_company_ids[batch_start:batch_start + self.BATCH_SIZE]
            self.stdout.write(f"Fetching batch {batch_start // self.BATCH_SIZE + 1} "
                              f"({len(batch)} companies)...")

            companies = self.get_companies_by_ids(batch)
            for c in companies:
                Company.objects.update_or_create(
                    igdb_company_id=c["id"],
                    defaults={"name": c["name"]},
                )

            self.stdout.write(f"Saved {len(batch)} companies in this batch.")
            sleep(0.1)  # optional gentle sleep

    # -------------------------
    # IGDB helpers
    # -------------------------

    def get_companies_by_ids(self, company_ids):
        if not company_ids:
            return []
        ids_str = ", ".join(str(i) for i in company_ids)
        query = f"fields id,name; where id = ({ids_str});"
        response = self.igdb.api_request("companies", query)
        data = self._decode_response(response)
        if not data:
            self.stdout.write(f"Warning: no company data returned for batch {company_ids[:5]}...")
        return data

    def _decode_response(self, response):
        if isinstance(response, bytes):
            return json.loads(response.decode("utf-8"))
        return response
