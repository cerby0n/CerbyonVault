interface CerbyonReducedProps {
  className?: string;
}

export default function CerbyonReduced({ className = "" }: CerbyonReducedProps) {
  return (<svg
          viewBox="0 0 369.6551724137931 60.46363814123745"
          className={className}
        >
          <g
            id="SvgjsG1857"
            transform="matrix(1.8857758620689655,0,0,1.8857758620689655,2.2480200076925344e-7,-0.05845905428126069)"
            fill="#00204a"
          >
            <path
              xmlns="http://www.w3.org/2000/svg"
              d="M16 .031l-.406.125-14.5 4-1.094.313v1.125c0 9.58 2.69 16.192 6.031 20.406 3.341 4.214 7.138 6.094 9.969 6.094 2.83 0 6.627-1.88 9.969-6.094 3.341-4.214 6.031-10.827 6.031-20.406v-1.125l-1.094-.313-14.5-4-.406-.125zm0 3.125v25.938c-1.27 0-4.741-1.301-7.625-4.938-2.752-3.471-5.068-9.098-5.281-17.438l12.906-3.563z"
            ></path>
          </g>
        </svg>); 
}