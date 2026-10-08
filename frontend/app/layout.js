import "./globals.css";

export const metadata = {
  title: "Todo App",
  description: "A full-stack Todo List application with AI-powered task suggestions",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
