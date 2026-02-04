import { Link } from "react-router";

const Footer = () => {
  return (
    <div className="bg-base-100 flex items-center justify-center text-center mx-auto max-w-7xl min-h-20">
      <span>
        Made by{" "}
        <Link
          to={"https://www.ccakir.com.tr/"}
          target="_blank"
          className="text-primary hover:text-secondary"
        >
          ccakirr
        </Link>{" "}
        |{" "}
        <Link
          to={"https://github.com/ccakirr"}
          target="_blank"
          className="text-primary hover:text-secondary"
        >
          View on GitHub
        </Link>{" "}
        | © 2025
      </span>
    </div>
  );
};

export default Footer;
