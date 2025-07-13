import { type NextRequest, NextResponse } from 'next/server'

export async function middleware(request: NextRequest) {
  // Redirect all routes to maintenance page except the maintenance page itself
  if (!request.nextUrl.pathname.startsWith('/maintenance')) {
    return NextResponse.redirect(new URL('/maintenance', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - api routes (for any API endpoints)
     */
    '/((?!_next/static|_next/image|favicon.ico|api).*)',
  ],
} 