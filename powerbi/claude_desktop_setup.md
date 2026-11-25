# Connect Claude Desktop to Power BI Desktop

This lets Claude edit the semantic model (tables, relationships, columns, measures) of a file open in Power BI Desktop. It does not create report pages or visuals; build those in Power BI Desktop using `dashboard_spec.md`.

Requirements: Windows, Power BI Desktop, the Claude Desktop app (the web chat cannot reach local files), and Node.js for the npx method.

## 1. Add the MCP server to Claude Desktop

In Claude Desktop: Settings > Developer > Edit Config. Add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "powerbi-modeling-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/powerbi-modeling-mcp@latest", "--start"]
    }
  }
}
```

If you already have other servers, add `powerbi-modeling-mcp` inside the existing `mcpServers` block. Save, then fully quit and reopen Claude Desktop.

Alternative if npx does not work: install the "Power BI Modeling MCP Server" extension in VS Code, then point `command` at the `powerbi-modeling-mcp.exe` inside the extension folder and use `"args": ["--start"]`.

## 2. Prepare the Power BI file

1. Open Power BI Desktop and create a blank report.
2. Save it as `aviation_dashboard.pbix` in the `powerbi` folder. Keep a copy before letting Claude change it.
3. Leave the file open. The server connects to the local model that Desktop runs, so the file must be open.

## 3. Ask Claude to build the model

Attach `powerbi/dashboard_spec.md` to a new Claude Desktop chat and paste:

```
Connect to 'aviation_dashboard' in Power BI Desktop.

Using the attached dashboard_spec.md, build the semantic model:
1. Create five tables from the Parquet files in
   D:\Aviation Project\aviation-analytics\powerbi\data
   using Power Query M, for example:
   let Source = Parquet.Document(File.Contents("D:\Aviation Project\aviation-analytics\powerbi\data\fact_flights.parquet")) in Source
   Tables: fact_flights, dim_airline, dim_airport, dim_date, dim_route.
2. Create the relationships in section 1 of the spec. Make the dest_airport relationship inactive.
3. Mark dim_date[full_date] as the date table. Set month_name to sort by month and day_name to sort by day_of_week.
4. Add the calculated column Dep Period to fact_flights.
5. Create a _Measures table and add every measure from section 3 of the spec, with the formats described there.
6. Run a few checks: Total Flights should be 2,303,556, and On-Time % should be about 80.5%.
Show me each change before you apply it.
```

Keep the confirmation prompts on (the default) so you see every change before it is applied.

## 4. Build the report pages

Build the five pages in Power BI Desktop from section 4 of `dashboard_spec.md`. Then send screenshots and the numbers will be checked against the SQL results.
