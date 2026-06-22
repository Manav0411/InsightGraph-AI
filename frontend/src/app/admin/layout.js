import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

export default async function AdminLayout({ children }) {
  const user = await currentUser();
  
  if (!user) {
    redirect('/');
  }

  const email = user.emailAddresses?.[0]?.emailAddress?.toLowerCase() || "";
  const adminEmails = process.env.ADMIN_EMAILS ? process.env.ADMIN_EMAILS.split(',') : [];
  
  const isAdmin = adminEmails.includes(email);

  if (!isAdmin) {
    redirect('/');
  }

  return (
    <div className="admin-subspace">
      {children}
    </div>
  );
}
