// Supabase Edge Function: quant-signals
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

    if (req.method === "POST") {
      const body = await req.json();
      const { ticker, signal, forecast_return_5d, confidence_score, composite_alpha_score, breakdown, consensus } = body;

      const { data, error } = await supabase.from("ai_signals").insert([
        {
          ticker: ticker || "AAPL",
          signal: signal || "BUY",
          forecast_return_5d: forecast_return_5d || 0.0284,
          confidence_score: confidence_score || 0.87,
          composite_alpha_score: composite_alpha_score || 0.76,
          factor_breakdown: breakdown || {},
          model_consensus: consensus || {},
        },
      ]).select();

      if (error) throw error;
      return new Response(JSON.stringify({ status: "success", inserted: data }), {
        headers: corsHeaders,
        status: 201,
      });
    }

    const { data, error } = await supabase
      .from("ai_signals")
      .select("*")
      .order("timestamp", { ascending: false })
      .limit(20);

    if (error) throw error;
    return new Response(JSON.stringify({ status: "success", signals: data }), {
      headers: corsHeaders,
      status: 200,
    });
  } catch (err: any) {
    return new Response(JSON.stringify({ status: "error", message: err.message }), {
      headers: corsHeaders,
      status: 500,
    });
  }
});
