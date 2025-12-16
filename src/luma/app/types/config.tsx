export interface Page {
  type: "page";
  title: string;
  path: string;
  section?: string;
}

export interface Link {
  type: "link";
  title: string;
  href: string;
}

export interface Reference {
  type: "reference";
  title: string;
  relative_path: string;
  apis: string[];
  section?: string;
}

export interface Section {
  type: "section";
  title: string;
  contents: (Page | Reference | Link)[];
}

export interface Tab {
  type: "tab";
  title: string;
  contents: (Page | Reference | Section | Link)[];
}

export type NavigationItem = Page | Reference | Section | Link | Tab;

export interface Social {
  platform: string;
  url: string;
}

export interface Config {
  name: string;
  favicon: string | null;
  navigation: NavigationItem[];
  socials?: Social[] | null;
}
