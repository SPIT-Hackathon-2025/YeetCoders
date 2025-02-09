import { Link } from "react-router-dom";
import {
  SignedIn,
  SignedOut,
  UserButton,
  SignInButton,
  SignOutButton,
  useUser,
} from "@clerk/clerk-react";

function Navbar() {
  const { isSignedIn, user } = useUser();

  return (
    <nav className="bg-white shadow-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Left Section - SVG Logo */}
          <div className="flex items-center flex-shrink-0">
            <Link to="/" className="flex items-center">
              {/* Wavy SVG Logo */}
              <svg
                width="40"
                height="40"
                viewBox="0 0 100 100"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M10 50 C20 20, 40 10, 60 50 S90 90, 100 50"
                  stroke="#4F46E5"
                  strokeWidth="6"
                  fill="none"
                  strokeLinecap="round"
                />
              </svg>
              <span className="ml-2 text-xl font-bold text-gray-800">
                PokéFlow
              </span>
            </Link>
          </div>

          {/* Center Section - Navigation Links */}
          <div className="flex space-x-6">
            <Link to="/" className="text-gray-700 hover:text-gray-900">
              Home
            </Link>
            <Link to="/features" className="text-gray-700 hover:text-gray-900">
              Features
            </Link>
            {isSignedIn ? (
              <Link to="/Templates" className="text-gray-700 hover:text-gray-900">
                Dashboard
              </Link>
            ) : (
              <SignInButton mode="modal">
                <button className="text-gray-700 hover:text-gray-900">
                  Dashboard
                </button>
              </SignInButton>
            )}
            {isSignedIn && (
              <Link to="/marketplace" className="text-gray-700 hover:text-gray-900">
                Marketplace
              </Link>
            )}
          </div>

          {/* Right Section - User Info & Auth Buttons */}
          <div className="flex items-center space-x-4">
            {isSignedIn ? (
              <>
                <span className="text-gray-700">
                  Welcome, {user.username || user.firstName}!
                </span>
                <SignOutButton>
                  <button className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                    Sign Out
                  </button>
                </SignOutButton>
                <div className="ml-2">
                  <UserButton />
                </div>
              </>
            ) : (
              <SignInButton mode="modal">
                <button className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                  Sign In
                </button>
              </SignInButton>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
