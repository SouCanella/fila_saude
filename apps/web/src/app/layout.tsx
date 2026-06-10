import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "FilaSaúde Brasil",
  description: "Filas de emergência hospitalares — piloto RJ",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
