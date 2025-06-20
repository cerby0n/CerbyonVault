import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import useAxios from "../axios/useAxios";
import TeamEditor from "../components/admin/TeamEditor";
import Sidebar from "../components/Sidebar";

export default function TeamDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const axiosInstance = useAxios();
  const [team, setTeam] = useState<any>(null);

  const fetchTeam = async () => {
    try {
      const res = await axiosInstance.get(`/teams/${id}/`);
      setTeam(res.data);
    } catch {
      navigate("/teams?tab=teams");
    }
  };

  useEffect(() => {
    fetchTeam();
  }, [id]);

  return team ? (
    <div className="flex min-h-screen overflow-hidden">
      <div className="shrink-0">
        <Sidebar />
      </div>
      <div className="flex flex-col min-w-0 w-full p-4">
        <TeamEditor
          team={team}
          onClose={() => navigate("/teams?tab=teams")}
          onSave={fetchTeam}
        />
      </div>
    </div>
  ) : (
    <p>Loading...</p>
  );
}
