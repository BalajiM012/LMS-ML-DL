import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { isAuthenticated, isAdmin } from '@/lib/jwt'

// Paths that don't require authentication
const publicPaths = [
  '/',
  '/login',
  '/api/auth/login',
]

// Paths that require admin access
const adminPaths = [
  '/admin',
  '/api/admin',
]

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname

  // Allow public paths
  if (publicPaths.some(p => path.startsWith(p))) {
    return NextResponse.next()
  }

  // Get token from cookie
  const token = request.cookies.get('token')?.value

  try {
    // Verify authentication
    const user = await isAuthenticated(token)

    // Check admin access for admin paths
    if (adminPaths.some(p => path.startsWith(p))) {
      const isAdminUser = await isAdmin(token)
      if (!isAdminUser) {
        return NextResponse.redirect(new URL('/login', request.url))
      }
    }

    // For student paths, verify the user is a student
    if (path.startsWith('/student') || path.startsWith('/api/student')) {
      if (user.role !== 'student') {
        return NextResponse.redirect(new URL('/login', request.url))
      }
    }

    // Add user info to headers for API routes
    if (path.startsWith('/api/')) {
      const requestHeaders = new Headers(request.headers)
      requestHeaders.set('Authorization', `Bearer ${token}`)

      return NextResponse.next({
        request: {
          headers: requestHeaders,
        },
      })
    }

    return NextResponse.next()
  } catch (error) {
    // Redirect to login for authentication errors
    return NextResponse.redirect(new URL('/login', request.url))
  }
}

// Configure middleware to run on specific paths
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
}
