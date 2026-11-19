// Public interface of @hodegos/discovery. The Node adapter is exported apart, from
// `@hodegos/discovery/node`, so that this entry imports no Node module.

export { DECLARATION_PLACES, FORMAT } from "./declaration.js";
export { discover, DOT_CONFIG, type Discovery, type Invocation } from "./discovery.js";
export { DiscoveryError, ERROR_CODES, type ErrorCode } from "./errors.js";
export type { FileSystem } from "./file-system.js";
export { rootVariable, type Tool } from "./tool.js";
