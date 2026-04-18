import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // If they hit the root domain barcias.com, redirect to company profile
  if (request.nextUrl.pathname === '/') {
    return NextResponse.redirect('https://www.realtyofamerica.com/real-estate-agents/Illinois/bernardo-jimenez')
  }
}