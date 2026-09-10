import { auth } from '@clerk/nextjs/server';
import IntelligenceReader from '../components/IntelligenceReader';
import Landing from '../components/landing/Landing';

export const metadata = {
  title: 'InsightGraph — your morning AI briefing',
  description:
    'A six-agent pipeline reads the AI ecosystem overnight, ranks it against your topics, and files one grounded briefing to your inbox by 8 AM.',
  openGraph: {
    title: 'InsightGraph — your morning AI briefing',
    description:
      'You slept. It read everything. Here are the twelve. A grounded daily AI briefing, tuned to your topics.',
    type: 'website',
  },
};

export default async function Home() {
  const { userId } = await auth();
  return userId ? <IntelligenceReader /> : <Landing />;
}
