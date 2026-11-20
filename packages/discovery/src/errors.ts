// Errors of the discovery, each carrying the code that the conformance cases name. The codes equal
// those of the Python implementation.

/** Kinds of failure of a discovery. */
export type ErrorCode =
  "invalid-request" | "missing-config" | "competing-places" | "invalid-pyproject";

/** Every kind of failure, in the order of their declaration. */
export const ERROR_CODES: readonly ErrorCode[] = [
  "invalid-request",
  "missing-config",
  "competing-places",
  "invalid-pyproject",
];

/** Failure of a discovery, with its kind and an actionable message. */
export class DiscoveryError extends Error {
  readonly code: ErrorCode;

  constructor(code: ErrorCode, message: string) {
    super(message);
    this.name = "DiscoveryError";
    this.code = code;
  }
}
