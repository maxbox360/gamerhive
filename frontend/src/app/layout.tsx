import "./globals.css";
import Header from "../components/Header";
import Providers from "../components/Providers";

export const metadata = {
  title: "GamerHive",
  description: "A hub for games and developers",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, backgroundColor: "#111", color: "#fff" }}>
        <Providers>
          <Header />
          <main style={{ paddingTop: "48px" }}>{children}</main>
        </Providers>
      </body>
    </html>
  );
}
