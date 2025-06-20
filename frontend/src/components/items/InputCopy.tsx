import { ClipboardWithIcon } from "flowbite-react";

type InputCopyProps={
    value:string
}

export function InputCopy({value}:InputCopyProps) {
  return (
    <div className="w-full max-w-auto">
      <div className=" relative items-center flex">
        <label htmlFor="npm-install" className="sr-only">
          Label
        </label>
        <input
          id="npm-install"
          type="text"
          className="truncate text-start col-span-6 block w-full pr-10 rounded-lg border border-neutral/50 bg-base-100 p-2.5 text-sm"
          value={value}
          disabled
          readOnly
        />
        <ClipboardWithIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 cursor-pointer" valueToCopy={value} />
      </div>
    </div>
  );
}