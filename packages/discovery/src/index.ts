// Public interface of @hodegos/discovery. The Node adapter is exported apart, from
// `@hodegos/discovery/node`, so that this entry imports no Node module.

export { CONFIG_FOLDERS, discover, type Discovery, type Invocation } from "./discovery.js";
export { DiscoveryError, ERROR_CODES, type ErrorCode } from "./errors.js";
export type { FileSystem } from "./file-system.js";
export { rootVariable, type Tool } from "./tool.js";
