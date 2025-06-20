import { useMemo } from "react";
import Select, { MultiValue } from "react-select";
import makeAnimated from "react-select/animated";

import { useQuery } from "@tanstack/react-query";
import { Team } from "../types";
import useAxios from "../axios/useAxios";

type Option = { value: number; label: string };

interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  teams: Team[];
}

interface TeamsSelectProps {
  value: Team[];
  onChange: (teams: Team[]) => void;
}

function TeamsSelect({ value, onChange }: TeamsSelectProps) {
  const axiosInstance = useAxios();

  const {
    data: user,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["user-me"],
    queryFn: async () => {
      const res = await axiosInstance.get<User>("/users/me/");
      return res.data;
    },
  });

  const allTeams = user?.teams ?? [];
  const animatedComponents = useMemo(() => makeAnimated(), []);

  const options: Option[] = useMemo(
    () => allTeams.map((t) => ({ value: t.id, label: t.name })),
    [allTeams]
  );

  const selectedOptions: Option[] = useMemo(
    () => options.filter((opt) => value.some((team) => team.id === opt.value)),
    [options, value]
  );

  const handleChange = (newOpts: MultiValue<Option>) => {
    const newIds = newOpts.map((o) => o.value);
    const newTeams = allTeams.filter((t) => newIds.includes(t.id));
    onChange(newTeams);
  };

  if (isLoading) return <div>Loading teams...</div>;
  if (error) return <div>Failed to load teams</div>;

  return (
    <Select<Option, true>
      name="teams"
      closeMenuOnSelect={true}
      options={options}
      components={animatedComponents}
      isMulti
      onChange={handleChange}
      className="text-gray-900"
      value={selectedOptions}
      styles={{
        menuList: (provided) => ({
          ...provided,
          maxHeight: 150,
          overflowY: "auto",
        }),
      }}
    />
  );
}

export default TeamsSelect;
