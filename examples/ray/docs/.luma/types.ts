interface PyArg {
  name: string;
  type: string | null;
  desc: string;
}

interface PyExample {
  desc: string | null;
  code: string;
}

export interface PyFunc {
  name: string;
  signature: string;
  summary: string;
  desc: string;
  args: PyArg[];
  returns: string | null;
  examples: PyExample[];
}
