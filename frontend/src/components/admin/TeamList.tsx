import { useEffect, useState } from "react";
import useAxios from "../../axios/useAxios";
import { useAuth } from "../../context/AuthContext";
import { useToast } from "../ToastProvider";
import TeamCard from "../items/TeamCard";
import { useNavigate } from "react-router-dom";
import CreateTeamModal from "../modals/CreateTeamModal";

export default function TeamList() {
  const axiosInstance = useAxios();
  const { user } = useAuth();
  const { notify } = useToast();
  const navigate = useNavigate();
  const [teams, setTeams] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState("all");
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchTeams = async () => {
    try {
      const res = await axiosInstance.get("/teams/");
      const data = Array.isArray(res.data) ? res.data : [];
      const enriched = data.map((team: any) => ({
        ...team,
        isCurrentUserMember: team.members.some(
          (m: any) => m.id === user?.user_id
        ),
      }));
      setTeams(enriched);
    } catch (error) {
      notify("❌ Failed to load teams", "error");
      console.log(error);
    }
  };

  useEffect(() => {
    fetchTeams();
  }, []);

  const filtered = teams
  .filter((team) => {
    const matchesSearch = team.name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesFilter =
      filter === "all" || (filter === "mine" && team.isCurrentUserMember);
    return matchesSearch && matchesFilter;
  })
  .sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="card p-4 w-full h-full">
      <div className="flex justify-between items-center mb-6 flex-wrap gap-2">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search group..."
            className="input input-bordered"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select
            className="select select-bordered"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All groups</option>
            <option value="mine">My groups</option>
          </select>
        </div>

        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          Create Team
        </button>
      </div>

      {/* Team Cards Grid */}

      <div
        className="
    grid
    grid-cols-[repeat(auto-fill,minmax(220px,1fr))]
    gap-6
    w-full
    pt-4
    list-none
    text-left
    select-text
  "
      >
        {filtered.map((team) => (
          <TeamCard
            key={team.id}
            team={team}
            onClick={() => navigate(`/admin/teams/${team.id}`)}
          />
        ))}
      </div>

      {showCreateModal && (
        <CreateTeamModal
          onClose={() => setShowCreateModal(false)}
          onCreated={() => {
            setShowCreateModal(false);
            fetchTeams(); // reload after creation
          }}
        />
      )}
    </div>
  );
}
