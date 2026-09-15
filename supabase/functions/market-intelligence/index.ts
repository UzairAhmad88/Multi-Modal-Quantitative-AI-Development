// Supabase Edge Function: market-intelligence
// Organization: szlgsmaolpgwjrvdgvut
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Content-Type": "application/json",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL") || "";
    const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY") || "";
    const supabase = createClient(supabaseUrl, supabaseAnonKey);

    const url = new URL(req.url);
    const ticker = url.searchParams.get("ticker") || "AAPL";
    const endpoint = url.searchParams.get("endpoint") || "overview";

    if (endpoint === "signals") {
      const { data, error } = await supabase
        .from("ai_signals")
        .select("*")
        .eq("ticker", ticker)
        .order("timestamp", { ascending: false })
        .limit(1);

      if (error) throw error;
      return new Response(JSON.stringify({ status: "success", ticker, signal: data[0] || null }), {
        headers: corsHeaders,
        status: 200,
      });
    }

    if (endpoint === "portfolio") {
      const { data, error } = await supabase
        .from("portfolio_allocations")
        .select("*")
        .order("timestamp", { ascending: false });

      if (error) throw error;
      return new Response(JSON.stringify({ status: "success", portfolio: data || [] }), {
        headers: corsHeaders,
        status: 200,
      });
    }

    if (endpoint === "risk") {
      const { data, error } = await supabase
        .from("risk_metrics")
        .select("*")
        .order("timestamp", { ascending: false })
        .limit(1);

      if (error) throw error;
      return new Response(JSON.stringify({ status: "success", risk: data[0] || null }), {
        headers: corsHeaders,
        status: 200,
      });
    }

    // Default overview response
    const { data: latestSignals } = await supabase.from("v_latest_signals").select("*");
    const { data: latestRisk } = await supabase.from("risk_metrics").select("*").limit(1);

    return new Response(
      JSON.stringify({
        status: "success",
        system: "QUANT AI - Multi-Modal Quantitative Intelligence",
        version: "v2.4.1",
        timestamp: new Date().toISOString(),
        signals: latestSignals || [],
        risk_summary: latestRisk[0] || null,
      }),
      { headers: corsHeaders, status: 200 }
    );
  } catch (err: any) {
    return new Response(JSON.stringify({ status: "error", message: err.message }), {
      headers: corsHeaders,
      status: 500,
    });
  }
});
