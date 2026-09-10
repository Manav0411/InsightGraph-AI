// Next 16 renamed the `middleware` file convention to `proxy` (Node runtime, no edge).
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// `/` is public — signed-out visitors get the marketing landing (src/app/page.js);
// signed-in visitors get the Intelligence Reader from the same route.
const isPublicRoute = createRouteMatcher(['/', '/sign-in(.*)', '/sign-up(.*)']);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
};
