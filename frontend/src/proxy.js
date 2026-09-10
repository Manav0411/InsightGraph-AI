// Next 16 renamed the `middleware` file convention to `proxy` (Node runtime, no edge).
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// `/` is public — signed-out visitors get the marketing landing (src/app/page.js);
// signed-in visitors get the Intelligence Reader from the same route.
// `/style-guide` is a dev-only primitives reference (404s in production) — public
// so `npm run dev` doesn't bounce it to sign-in.
const isPublicRoute = createRouteMatcher(['/', '/style-guide', '/sign-in(.*)', '/sign-up(.*)']);

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
