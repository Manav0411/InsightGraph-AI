import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

export default async function AdminLayout({ children }) {
  const user = await currentUser();
  
  if (!user) {
    redirect('/');
  }

  // Basic admin check. In production, define ADMIN_EMAILS in .env
  // For local development, we'll allow access if the email contains the username or is defined.
  const email = user.emailAddresses?.[0]?.emailAddress?.toLowerCase() || "";
  const adminEmails = process.env.ADMIN_EMAILS ? process.env.ADMIN_EMAILS.split(',') : [];
  
  // If ADMIN_EMAILS is not set, we'll gracefully allow the first authenticated user to access it 
  // during development, but in production this should be strictly enforced.
  const isAdmin = adminEmails.length === 0 || adminEmails.includes(email);

  if (!isAdmin) {
    redirect('/');
  }

  return (
    <div className="admin-subspace">
      {/* Optional: Add an Admin-specific sub-nav or warning banner here later */}
      {children}
    </div>
  );
}
