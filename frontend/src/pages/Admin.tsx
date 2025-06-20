import UserList from "../components/admin/UserList";
import Sidebar from "../components/Sidebar";
import TeamList from "../components/admin/TeamList";
import { RiTeamFill } from "react-icons/ri";
import { FaUser } from "react-icons/fa6";
import { useSearchParams } from "react-router-dom";


export default function Admin() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTab = searchParams.get("tab") || "members";

  return (
    <div className="flex min-h-screen overflow-hidden">
      <div className="shrink-0">
        <Sidebar />
      </div>
      <div className="flex min-w-0 w-full p-4 pl-0 ">
        <div className="tabs tabs-border tabs-x rounded w-full bg-base-100 mb-4">
          <label className="tab text-xl">
            <input
              type="radio"
              name="admin_tabs"
              checked={currentTab === "members"}
              onChange={() => setSearchParams({ tab: "members" })}
            />
            <FaUser className="me-2" size={20} />
            Members
          </label>

          <div className="tab-content">
            {currentTab === "members" && <UserList />}
          </div>
          <label className="tab text-xl">
            <input
              type="radio"
              name="admin_tabs"
              checked={currentTab === "teams"}
              onChange={() => setSearchParams({ tab: "teams" })}
            />
            <RiTeamFill className="me-2" size={23} />
            Teams
          </label>
          <div className="tab-content">
            {currentTab === "teams" && <TeamList />}
          </div>
        </div>
      </div>
    </div>
  );
}
