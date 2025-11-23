import "./globals.css";
import { ThemeProvider } from "@/lib/theme";

export const metadata = {
  title: "Company Policy Assistant",
  description: "Internal AI assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
