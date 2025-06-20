type Props = {
  onClick: () => void;
  label: string;
};

export default function CustomMenuButton({ onClick, label }: Props) {
  return (
    <button
      onClick={onClick}
      className="cursor-pointer w-full text-start p-1 hover:bg-gray-100 rounded"
    >
      {label}
    </button>
  );
}