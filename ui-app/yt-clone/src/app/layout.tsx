import type { Metadata } from "next";
import "./globals.css";
import HeaderBar from "./components/headerbar/headerbar";

export const metadata: Metadata = {
  title: "Video platform service clone.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={``}
      >
        <HeaderBar />
        {children}
      </body>
    </html>
  );
}
