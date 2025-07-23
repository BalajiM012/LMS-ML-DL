import React from "react"
import Link from "next/link"
import { Card, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"

export default function HomePage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen gap-8 p-4 bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold">Welcome to</h1>
        <p className="text-2xl mt-2">Library Management System Website</p>
      </div>
      <div className="flex flex-col gap-6">
        <Card className="w-64 flex flex-col items-center p-6 border rounded-lg shadow-md bg-white">
          <CardTitle className="mb-4">Student</CardTitle>
          <div className="flex flex-col gap-4 w-full">
            <Link href="/student_login.html" legacyBehavior passHref>
              <Button asChild>
                <a className="w-full">Login</a>
              </Button>
            </Link>
            <Link href="/student_signup.html" legacyBehavior passHref>
              <Button asChild>
                <a className="w-full">Sign Up</a>
              </Button>
            </Link>
          </div>
        </Card>
        <Card className="w-64 flex flex-col items-center p-6 border rounded-lg shadow-md bg-white">
          <CardTitle className="mb-4">Admin</CardTitle>
          <div className="flex flex-col gap-4 w-full">
            <Link href="/admin_login.html" legacyBehavior passHref>
              <Button asChild>
                <a className="w-full">Login</a>
              </Button>
            </Link>
            <Link href="/admin_signup.html" legacyBehavior passHref>
              <Button asChild>
                <a className="w-full">Sign Up</a>
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </main>
  )
}
