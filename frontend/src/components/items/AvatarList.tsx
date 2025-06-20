interface User {
  id: number;
  first_name: string;
  last_name: string;
}
interface Team {
  id: number;
  name: string;
  created_at: string;
  members: User[];
  isCurrentUserMember?: boolean;
}
interface AvatarListProps {
  team: Team;
}

const AvatarList = ({team}:AvatarListProps) => {
  const members = team?.members || [];

  const getInitials = (user: User): string => {
    const firstInitial = user.first_name?.charAt(0).toUpperCase() || "";
    const lastInitial = user.last_name?.charAt(0).toUpperCase() || "";
    return firstInitial + lastInitial;
  };

  return (
    
    <ul className="flex -space-x-4 mb-2">
      {members.slice(0, 4).map((member, idx) => (
        <li
          key={idx}
          className={`relative z-${40 - idx * 10} w-15 h-15 rounded-full border-3 border-base-100 flex items-center justify-center bg-accent text-accent-content text-xl font-semibold`}
          title={member.last_name}
        >
          {getInitials(member)}
        </li>
      ))}
      {members.length > 4 && (
        <li className="relative w-15 h-15 border-3 border-base-100 rounded-full flex items-center justify-center bg-accent text-accent-content text-xl font-semibold">
          +{members.length - 4}
        </li>
      )}
    </ul>

  );
};

export default AvatarList;