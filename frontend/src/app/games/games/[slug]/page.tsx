import { redirect } from "next/navigation";

export default async function LegacyGameDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  redirect(`/games/${encodeURIComponent(slug)}`);
}
