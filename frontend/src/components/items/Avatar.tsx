interface AvatarProps {
  firstname?: string;
  lastname?: string;
  size?: number;
  textSize?: number;
}

export const Avatar = ({ firstname = "", lastname = "",size=45, textSize = 20 }: AvatarProps) => {
  const firstInitial = firstname?.charAt(0).toUpperCase() ?? "";
  const lastInitial = lastname?.charAt(0).toUpperCase() ?? "";
  const initials = `${firstInitial}${lastInitial}`;
  return (
    <div className="avatar avatar-placeholder">
      <div className="bg-accent font-semibold text-accent-content rounded-full" style={{ width: size, height: size }}>
        <span style={{ fontSize: textSize }}>{initials}</span>
      </div>
    </div>
  );
};
