export interface Page {
  type: "page";
  title: string;
  path: string;
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
}

export interface Section {
  type: "section";
  title: string;
  contents: (Page | Reference | Link)[];
}

export type NavigationItem = Page | Reference | Section | Link;

export interface Config {
  name: string;
  favicon: string | null;
  navigation: NavigationItem[];
}
