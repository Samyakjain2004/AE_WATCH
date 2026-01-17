// import React, { useEffect, useRef } from "react";
// import {
//   Chart as ChartJS,
//   CategoryScale,
//   LinearScale,
//   BarElement,
//   Title,
//   Tooltip,
//   Legend,
// } from "chart.js";
// import { Bar } from "react-chartjs-2";
// import { TrendingUp } from "lucide-react";

// // Register Chart.js components
// ChartJS.register(
//   CategoryScale,
//   LinearScale,
//   BarElement,
//   Title,
//   Tooltip,
//   Legend
// );

// const FAERSChart = ({ data }) => {
//   if (
//     !data ||
//     !data.faers_data ||
//     !data.faers_data.details ||
//     data.faers_data.details.length === 0
//   ) {
//     return (
//       <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border shadow-sm p-5">
//         <h2 className="font-semibold text-foreground mb-4 flex items-center">
//           <TrendingUp size={18} className="mr-2" style={{ color: '#166E39' }} />
//           FAERS Report Distribution
//         </h2>
//         <div className="text-center py-8 text-muted-foreground text-sm">
//           No FAERS data available. Upload an audio file with detected
//           medications to see the comparison.
//         </div>
//       </div>
//     );
//   }

//   // Prepare data for chart
//   const faersDetails = data.faers_data.details.slice(0, 5); // Top 5
//   const labels = faersDetails.map((d) => `${d.drug}\n+ ${d.symptom}`);
//   const reportCounts = faersDetails.map((d) => d.reports);

//   // Calculate patient's symptom frequencies if available
//   const patientSymptoms = {};
//   if (data.entities) {
//     data.entities.forEach((entity) => {
//       if (entity.Category === "MEDICAL_CONDITION") {
//         patientSymptoms[entity.Text.toLowerCase()] = entity.Frequency || 1;
//       }
//     });
//   }

//   const chartData = {
//     labels: labels,
//     datasets: [
//       {
//         label: "FAERS Reports",
//         data: reportCounts,
//         backgroundColor: "rgba(40, 125, 73, 0.7)", // #287D49 with opacity
//         borderColor: "rgba(22, 110, 57, 1)",      // #166E39
//         borderWidth: 2,
//         borderRadius: 6,
//         hoverBackgroundColor: "rgba(30, 92, 26, 0.8)", // #1E5C1A
//       },
//     ],
//   };

//   const options = {
//     responsive: true,
//     maintainAspectRatio: false,
//     plugins: {
//       legend: {
//         display: true,
//         position: "top",
//         labels: {
//           color: "hsl(222.2, 84%, 4.9%)",
//           font: {
//             size: 12,
//             family: "Inter, sans-serif",
//           },
//         },
//       },
//       title: {
//         display: false,
//       },
//       tooltip: {
//         backgroundColor: "rgba(22, 110, 57, 0.9)", // #166E39 based
//         titleColor: "#fff",
//         bodyColor: "#fff",
//         borderColor: "rgba(255, 255, 255, 0.2)",
//         borderWidth: 1,
//         padding: 12,
//         displayColors: true,
//         callbacks: {
//           label: function (context) {
//             return `Reports: ${context.parsed.y.toLocaleString()}`;
//           },
//         },
//       },
//     },
//     scales: {
//       y: {
//         beginAtZero: true,
//         ticks: {
//           color: "hsl(215.4, 16.3%, 46.9%)",
//           font: {
//             size: 11,
//           },
//           callback: function (value) {
//             if (value >= 1000) {
//               return (value / 1000).toFixed(1) + "k";
//             }
//             return value;
//           },
//         },
//         grid: {
//           color: "rgba(0, 0, 0, 0.05)",
//         },
//       },
//       x: {
//         ticks: {
//           color: "hsl(215.4, 16.3%, 46.9%)",
//           font: {
//             size: 10,
//           },
//           maxRotation: 45,
//           minRotation: 45,
//         },
//         grid: {
//           display: false,
//         },
//       },
//     },
//   };

//   return (
//     <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border shadow-sm p-5">
//       <h2 className="font-semibold text-foreground mb-4 flex items-center">
//         <TrendingUp size={18} className="mr-2" style={{ color: '#166E39' }} />
//         FAERS Report Distribution
//       </h2>
//       <p className="text-xs text-muted-foreground mb-4">
//         Comparing identified drug-symptom pairs with FDA adverse event database
//       </p>
//       <div style={{ height: "250px" }}>
//         <Bar data={chartData} options={options} />
//       </div>
//       <div className="mt-4 text-xs text-muted-foreground">
//         <p>
//           ℹ️ Higher report counts indicate more frequent adverse events recorded
//           in FAERS database.
//         </p>
//       </div>
//     </div>
//   );
// };

// export default FAERSChart;

import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { BarChart3 } from "lucide-react";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const FAERSChart = ({ data }) => {
  // 1. Check for the new JSON structure
  const events = data?.summary?.suspected_adverse_events;

  if (!events || events.length === 0) {
    return (
      <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border shadow-sm p-5">
        <h2 className="font-semibold text-foreground mb-4 flex items-center">
          <BarChart3 size={18} className="mr-2" style={{ color: '#166E39' }} />
          FAERS Signal Analysis
        </h2>
        <div className="text-center py-8 text-muted-foreground text-sm italic">
          Awaiting analysis result to plot safety signals...
        </div>
      </div>
    );
  }

  // 2. Prepare Data: Map event names to labels and ROR scores to data
  const labels = events.map((e) => e.event_meddra_pt);
  const rorScores = events.map((e) => e.faers_signal.ror_lcl95);
  // We use Serious Fraction for the color intensity (Darker = More Serious)
  const seriousFractions = events.map((e) => e.faers_signal.serious_fraction);

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: "Reporting Odds Ratio (ROR)",
        data: rorScores,
        // Dynamic coloring: Higher serious fraction = redder bar
        backgroundColor: seriousFractions.map(sf => 
          sf > 0.85 ? "rgba(220, 38, 38, 0.7)" : "rgba(40, 125, 73, 0.7)"
        ),
        borderColor: seriousFractions.map(sf => 
          sf > 0.85 ? "rgb(220, 38, 38)" : "rgb(22, 110, 57)"
        ),
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#1e293b",
        padding: 12,
        callbacks: {
          afterLabel: (context) => {
            const index = context.dataIndex;
            const serious = (events[index].faers_signal.serious_fraction * 100).toFixed(0);
            const count = events[index].faers_signal.nDE;
            return `Serious Fraction: ${serious}%\nTotal Database Cases: ${count}`;
          }
        }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'ROR Score', font: { weight: 'bold', size: 10 } },
        grid: { color: "rgba(0,0,0,0.05)" }
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 10, weight: '600' } }
      }
    },
  };

  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-bold text-slate-800 flex items-center">
          <BarChart3 size={18} className="mr-2 text-emerald-700" />
          FAERS Safety Signal Magnitude
        </h2>
        <span className="text-[10px] font-black bg-slate-100 text-slate-500 px-2 py-1 rounded-md uppercase tracking-wider">
          ROR LCL95 Metrics
        </span>
      </div>
      
      <div style={{ height: "240px" }}>
        <Bar data={chartData} options={options} />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 border-t pt-4">
        <div className="flex items-start gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-600 mt-1" />
          <p className="text-[10px] text-slate-500 leading-tight">
            <strong>ROR Score:</strong> Measures if an event is reported more frequently for this drug than expected.
          </p>
        </div>
        <div className="flex items-start gap-2">
          <div className="w-2 h-2 rounded-full bg-red-600 mt-1" />
          <p className="text-[10px] text-slate-500 leading-tight">
            <strong>Serious %:</strong> Fraction of cases in the FDA database resulting in hospitalization or death.
          </p>
        </div>
      </div>
    </div>
  );
};

export default FAERSChart;  