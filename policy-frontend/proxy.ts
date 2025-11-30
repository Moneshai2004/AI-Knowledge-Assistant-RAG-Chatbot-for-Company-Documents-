import { NextResponse } from "next/server";

export function proxy(request: Request) {
  const url = new URL(request.url);
  const pathname = url.pathname;

  if (pathname.startsWith("/admin")) {
    const cookieHeader = request.headers.get("cookie") || "";

    const cookieToken = cookieHeader
      .split(";")
      .find((c) => c.trim().startsWith("token="));

    if (!cookieToken) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"],
};
