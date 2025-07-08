import "@livekit/components-styles";
import { Metadata } from "next";
import { Public_Sans } from "next/font/google";
import Header from "@/components/Header";
import { PostHogProvider } from "@/components/PostHogProvider";
import "./globals.css";

const publicSans400 = Public_Sans({
  weight: "400",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI IELTS Examiner - Premium Learning Platform",
  description:
    "Transform your IELTS speaking skills with AI-powered personalized coaching and real-time feedback.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`h-full ${publicSans400.className}`}>
      <body className="h-full flex flex-col bg-gray-900 text-gray-100 antialiased">
        <PostHogProvider>
          <Header />
          <main className="flex-1 bg-gray-900 pt-20">{children}</main>
        </PostHogProvider>
      </body>
    </html>
  );
}
