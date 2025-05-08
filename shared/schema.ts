import { pgTable, text, serial, integer, boolean, timestamp, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// User table for auth
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

// Screenshots table to store captured screen data
export const screenshots = pgTable("screenshots", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  timestamp: timestamp("timestamp").notNull().defaultNow(),
  fullScreenPath: text("full_screen_path").notNull(),
  mouseAreaPath: text("mouse_area_path").notNull(),
  mouseX: integer("mouse_x").notNull(),
  mouseY: integer("mouse_y").notNull(),
  activeWindow: text("active_window"),
  activeApplication: text("active_application"),
  extractedText: text("extracted_text"),
  confidence: integer("confidence"),
});

export const insertScreenshotSchema = createInsertSchema(screenshots).omit({
  id: true,
  timestamp: true,
});

// Activity logs table
export const activityLogs = pgTable("activity_logs", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  timestamp: timestamp("timestamp").notNull().defaultNow(),
  activityType: text("activity_type").notNull(), // 'mouse_click', 'keyboard', 'application', etc.
  description: text("description").notNull(),
  data: jsonb("data"), // Additional data specific to the activity type
  screenshotId: integer("screenshot_id").references(() => screenshots.id),
});

export const insertActivityLogSchema = createInsertSchema(activityLogs).omit({
  id: true,
  timestamp: true,
});

// Automation tasks table
export const automationTasks = pgTable("automation_tasks", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  name: text("name").notNull(),
  description: text("description"),
  steps: jsonb("steps").notNull(), // Array of steps to perform
  triggers: jsonb("triggers").notNull(), // What triggers this automation
  executionCount: integer("execution_count").notNull().default(0),
  lastExecuted: timestamp("last_executed"),
  isActive: boolean("is_active").notNull().default(true),
});

export const insertAutomationTaskSchema = createInsertSchema(automationTasks).omit({
  id: true,
  executionCount: true,
  lastExecuted: true,
});

// Settings table
export const settings = pgTable("settings", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id).notNull(),
  captureInterval: integer("capture_interval").notNull().default(1000), // in milliseconds
  keepHistoryDays: integer("keep_history_days").notNull().default(7),
  enableKeyLogging: boolean("enable_key_logging").notNull().default(true),
  enableScreenCapture: boolean("enable_screen_capture").notNull().default(true),
  enableAutomationSuggestions: boolean("enable_automation_suggestions").notNull().default(true),
  sidebarPosition: text("sidebar_position").notNull().default("right"),
  theme: text("theme").notNull().default("light"),
});

export const insertSettingsSchema = createInsertSchema(settings).omit({
  id: true,
});

// Export types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;

export type Screenshot = typeof screenshots.$inferSelect;
export type InsertScreenshot = z.infer<typeof insertScreenshotSchema>;

export type ActivityLog = typeof activityLogs.$inferSelect;
export type InsertActivityLog = z.infer<typeof insertActivityLogSchema>;

export type AutomationTask = typeof automationTasks.$inferSelect;
export type InsertAutomationTask = z.infer<typeof insertAutomationTaskSchema>;

export type Settings = typeof settings.$inferSelect;
export type InsertSettings = z.infer<typeof insertSettingsSchema>;
