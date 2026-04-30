import "./globals.css";

export const metadata = {
  title: "AI HR Policy Assistant",
  description: "Strict, document-grounded HR assistant answering employee queries based on uploaded company policies.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
