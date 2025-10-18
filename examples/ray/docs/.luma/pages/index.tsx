import { GetServerSideProps } from "next";

import configData from "../data/config.json";
import { Config, NavigationItem } from "../types/config";
const config = configData as Config;

export const getServerSideProps: GetServerSideProps = async () => {
  let destination = "/";

  if (config && config.navigation && config.navigation.length > 0) {
    destination = getFirstPage(config.navigation);
  }

  return {
    redirect: {
      destination,
      permanent: false,
    },
  };
};

function getFirstPage(navigation: NavigationItem[]): string {
  for (const item of navigation) {
    if (item.type == "page") {
      return `/${item.path.slice(0, -3)}`;
    } else if (item.type == "section") {
      return getFirstPage(item.contents);
    } else if (item.type == "reference") {
      return item.relative_path;
    }
  }

  return "/";
}

export default function Home() {
  return null;
}
