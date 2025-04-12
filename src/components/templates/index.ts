// Export all templates
export { DashboardTemplate } from "./DashboardTemplate";
export { JobsTemplate } from "./JobsTemplate";
export { ProfileTemplate } from "./ProfileTemplate";
export { MatchesTemplate } from "./MatchesTemplate";
export { AnalyticsTemplate } from "./AnalyticsTemplate";

// Default export for potential dynamic imports
export default {
  DashboardTemplate: () =>
    import("./DashboardTemplate").then((mod) => mod.DashboardTemplate),
  JobsTemplate: () => import("./JobsTemplate").then((mod) => mod.JobsTemplate),
  ProfileTemplate: () =>
    import("./ProfileTemplate").then((mod) => mod.ProfileTemplate),
  MatchesTemplate: () =>
    import("./MatchesTemplate").then((mod) => mod.MatchesTemplate),
  AnalyticsTemplate: () =>
    import("./AnalyticsTemplate").then((mod) => mod.AnalyticsTemplate),
};
