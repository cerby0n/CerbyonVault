import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import useAxios from "../axios/useAxios";
import CerbyonLogo from "../assets/CerbyonLogo";
import ThemeToggle from "../utils/ThemeToggle";

export default function Register() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm_password, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const axiosInstance = useAxios();

  useEffect(() => {
    const loadEmail = async () => {
      try {
        const res = await axiosInstance.get(`/register/${token}/`);
        setEmail(res.data.email);
      } catch (err) {
        setError("This invite link is invalid or expired.");
      }
    };
    if (token) loadEmail();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await axiosInstance.post(`/register/${token}/`, {
        username,
        first_name,
        last_name,
        password,
        confirm_password,
      });
      navigate("/login");
    } catch (err: any) {
      if (err.response?.data) {
        const messages = Object.values(err.response.data).join(" ");
        setError(messages);
      } else {
        setError("An unknown error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-base-200">
      <div className="w-full max-w-md p-6 bg-base-100 shadow-lg rounded-lg relative">
        <div className="absolute top-4 right-4">
          <ThemeToggle />
        </div>
        <div className="flex justify-center mt-10 mb-5">
          <CerbyonLogo className="h-16" />
        </div>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-semibold text-neutral mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              readOnly
              className="w-full px-4 py-2 border border-neutral rounded-md bg-base-300"
            />
          </div>

          <div className="mb-2">
            <label className="block text-sm font-semibold text-neutral mb-1">
              Username
            </label>

            <input
              type="text"
              required
              value={username}
              pattern="[A-Za-z][A-Za-z0-9\-]*"
              minLength={3}
              maxLength={30}
              onChange={(e) => setUsername(e.target.value)}
              className="input input-bordered w-full"
            />
          </div>

          <div className="flex gap-2 mb-2">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-neutral mb-1">
                First Name
              </label>
              <input
                type="text"
                required
                value={first_name}
                onChange={(e) => setFirstName(e.target.value)}
                className="input input-bordered w-full"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-semibold text-neutral mb-1">
                Last Name
              </label>
              <input
                type="text"
                required
                value={last_name}
                onChange={(e) => setLastName(e.target.value)}
                className="input input-bordered w-full"
              />
            </div>
          </div>

          <div className="mb-2">
            <label className="block text-sm font-semibold text-neutral mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input input-bordered w-full"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-semibold text-neutral mb-1">
              Confirm Password
            </label>
            <input
              type="password"
              required
              value={confirm_password}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="input input-bordered w-full"
            />
          </div>
          {error && (
            <div className="alert alert-error rounded-md text-sm mb-4">
              {error}
            </div>
          )}
          <button
            type="submit"
            className={`w-full py-2 bg-primary text-primary-content font-bold rounded-md hover:bg-primary-focus transition ${
              loading ? "opacity-50 cursor-not-allowed" : ""
            }`}
            disabled={loading || password.length < 8}
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>
      </div>
    </div>
  );
}
