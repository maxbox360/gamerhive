import "./globals.css";
import Header from "../components/Header";

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
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}
