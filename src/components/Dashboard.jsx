
// import React, { useState, useEffect } from "react";
// import {
//   FileAudio,
//   FileText,
//   AlertTriangle,
//   ArrowRight,
//   Clock,
//   ChevronRight,
//   AlertCircle,
// } from "lucide-react";
// import { motion } from "framer-motion";
// import { getSessionStats, getAnalysisHistory } from "../utils/sessionManager";

// const Dashboard = ({ onNavigate }) => {
//   const [stats, setStats] = useState({
//     totalCalls: 0,
//     emergentCalls:0,
//     criticalCalls: 0,
//     moderateCalls: 0,
//     lowRiskCalls: 0,

//   });
//   const [recentCalls, setRecentCalls] = useState([]);

//   useEffect(() => {
//     const loadStats = () => {
//       const sessionStats = getSessionStats();
//       setStats(sessionStats);

//       const history = getAnalysisHistory();
//       setRecentCalls(history.slice(0, 5));
//     };

//     loadStats();
//     const interval = setInterval(loadStats, 2000);
//     return () => clearInterval(interval);
//   }, []);

//   const container = {
//     hidden: { opacity: 0 },
//     show: {
//       opacity: 1,
//       transition: { staggerChildren: 0.1 },
//     },
//   };

//   const item = {
//     hidden: { opacity: 0, y: 20 },
//     show: { opacity: 1, y: 0 },
//   };

//   const getRiskColor = (level) => {
//     switch (level) {
//       case "Critical":
//         return "text-red-600 bg-red-50 border-red-200";
//       case "Moderate":
//         return "text-yellow-600 bg-yellow-50 border-yellow-200";
//       case "Low Risk":
//         return "text-emerald-600 bg-emerald-50 border-emerald-200";
//       default:
//         return "text-gray-600 bg-gray-50 border-gray-200";
//     }
//   };

//   const formatTimestamp = (isoString) => {
//     const date = new Date(isoString);
//     const now = new Date();
//     const diffMs = now - date;
//     const diffMins = Math.floor(diffMs / 60000);

//     if (diffMins < 1) return "Just now";
//     if (diffMins < 60) return `${diffMins} min ago`;
//     return `${Math.floor(diffMins / 60)} hours ago`;
//   };

//   return (
//     <motion.div
//       variants={container}
//       initial="hidden"
//       animate="show"
//       className="space-y-6"
//     >
//       <div className="flex items-center justify-between">
//         <motion.h1
//           variants={item}
//           className="text-2xl font-bold text-foreground"
//         >
//           Dashboard Overview
//         </motion.h1>
//         <motion.button
//           variants={item}
//           whileHover={{ scale: 1.05 }}
//           whileTap={{ scale: 0.95 }}
//           onClick={() => onNavigate("call-analysis")}
//           style={{ background: 'linear-gradient(to right, #166E39, #287D49)' }}
//           className="px-4 py-2 text-white rounded-lg hover:shadow-lg hover:shadow-green-900/20 transition-all font-medium flex items-center space-x-2"
//         >
//           <span>Analyze New Call</span>
//           <ArrowRight size={16} />
//         </motion.button>
//       </div>

//       {/* Session Stats Grid */}
//       <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
//         <motion.div
//           variants={item}
//           className="bg-card/50 backdrop-blur-sm p-6 rounded-xl border border-border shadow-sm hover:shadow-md transition-shadow"
//         >
//           <div className="flex items-center justify-between mb-4">
//             <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
//               <FileAudio size={24} />
//             </div>
//           </div>
//           <h3 className="text-2xl font-bold text-foreground">
//             {stats.totalCalls}
//           </h3>
//           <p className="text-sm text-muted-foreground">Calls Analyzed</p>
//         </motion.div>

//         <motion.div
//           variants={item}
//           className="bg-card/50 backdrop-blur-sm p-6 rounded-xl border border-border shadow-sm hover:shadow-md transition-shadow"
//         >
//           <div className="flex items-center justify-between mb-4">
//             <div className="p-3 bg-red-50 text-red-600 rounded-lg">
//               <AlertTriangle size={24} />
//             </div>
//           </div>
//           <h3 className="text-2xl font-bold text-foreground">
//             {stats.criticalCalls}
//           </h3>
//           <p className="text-sm text-muted-foreground">Emergent Adverse Event</p>
//         </motion.div>

//         <motion.div
//           variants={item}
//           className="bg-card/50 backdrop-blur-sm p-6 rounded-xl border border-border shadow-sm hover:shadow-md transition-shadow"
//         >
//           <div className="flex items-center justify-between mb-4">
//             <div className="p-3 bg-orange-50 text-orange-600 rounded-lg">
//               <AlertCircle size={24} />
//             </div>
//           </div>
//           <h3 className="text-2xl font-bold text-foreground">
//             {stats.criticalCalls}
//           </h3>
//           <p className="text-sm text-muted-foreground">Urgent Adverse Event</p>
//         </motion.div>

//         <motion.div
//           variants={item}
//           className="bg-card/50 backdrop-blur-sm p-6 rounded-xl border border-border shadow-sm hover:shadow-md transition-shadow"
//         >
//           <div className="flex items-center justify-between mb-4">
//             <div className="p-3 bg-yellow-50 text-yellow-600 rounded-lg">
//               <FileText size={24} />
//             </div>
//           </div>
//           <h3 className="text-2xl font-bold text-foreground">
//             {stats.moderateCalls}
//           </h3>
//           <p className="text-sm text-muted-foreground">Need Review</p>
//         </motion.div>

//         <motion.div
//           variants={item}
//           className="bg-card/50 backdrop-blur-sm p-6 rounded-xl border border-border shadow-sm hover:shadow-md transition-shadow"
//         >
//           <div className="flex items-center justify-between mb-4">
//             <div className="p-3 bg-green-50 text-green-600 rounded-lg">
//               <FileText size={24} />
//             </div>
//           </div>
//           <h3 className="text-2xl font-bold text-foreground">
//             {stats.lowRiskCalls}
//           </h3>
//           <p className="text-sm text-muted-foreground">Monitor</p>
//         </motion.div>
//       </div>

//       {/* Recent Analyses */}
//       <motion.div
//         variants={item}
//         className="bg-card/50 backdrop-blur-sm rounded-xl border border-border shadow-sm overflow-hidden"
//       >
//         <div className="p-6 border-b border-border flex items-center justify-between">
//           <h2 className="text-lg font-semibold text-foreground">
//             Recent Analysis
//           </h2>
//           <button
//             onClick={() => onNavigate("history")}
//             style={{ color: '#166E39' }}
//             className="text-sm font-medium hover:underline"
//           >
//             View All
//           </button>
//         </div>

//         {recentCalls.length === 0 ? (
//           <div className="p-12 text-center">
//             <FileAudio
//               size={48}
//               className="mx-auto text-muted-foreground opacity-20 mb-4"
//             />
//             <p className="text-muted-foreground mb-4">
//               No calls analyzed yet this session
//             </p>
//             <button
//               onClick={() => onNavigate("call-analysis")}
//               style={{ backgroundColor: '#166E39' }}
//               className="px-4 py-2 text-white rounded-lg hover:opacity-90 transition-colors"
//             >
//               Analyze Your First Call
//             </button>
//           </div>
//         ) : (
//           <div className="divide-y divide-border">
//             {recentCalls.map((call) => (
//               <div
//                 key={call.id}
//                 onClick={() => {
//                   onNavigate("call-analysis", call);
//                 }}
//                 className="p-4 hover:bg-accent/50 transition-colors flex items-center justify-between group cursor-pointer"
//               >
//                 <div className="flex items-center space-x-4 flex-1 min-w-0">
//                   <div 
//                     className="p-2 rounded-lg flex-shrink-0"
//                     style={{ backgroundColor: 'rgba(22, 110, 57, 0.1)' }}
//                   >
//                     <FileAudio size={20} style={{ color: '#166E39' }} />
//                   </div>
//                   <div className="flex-1 min-w-0">
//                     <h4 className="font-medium text-foreground truncate">
//                       {call.fileName}
//                     </h4>
//                     <div className="flex items-center text-xs text-muted-foreground mt-1">
//                       <Clock size={12} className="mr-1" />
//                       {formatTimestamp(call.timestamp)}
//                     </div>
//                   </div>
//                 </div>
//                 <div className="flex items-center space-x-4 flex-shrink-0">
//                   <div className="text-right mr-2">
//                     <div className="text-lg font-bold text-foreground">
//                       {call.riskScore}
//                     </div>
//                     <div
//                       className={`text-xs px-2 py-1 rounded-full border ${getRiskColor(
//                         call.riskLevel
//                       )}`}
//                     >
//                       {call.riskLevel}
//                     </div>
//                   </div>
//                   <ChevronRight
//                     size={18}
//                     className="text-muted-foreground group-hover:text-emerald-600 transition-colors"
//                   />
//                 </div>
//               </div>
//             ))}
//           </div>
//         )}
//       </motion.div>
//     </motion.div>
//   );
// };

// export default Dashboard;

import React, { useState, useEffect } from "react";
import {
  FileAudio,
  FileText,
  AlertTriangle,
  ArrowRight,
  Clock,
  ChevronRight,
  AlertCircle,
} from "lucide-react";
import { motion } from "framer-motion";
import { getSessionStats, getAnalysisHistory } from "../utils/sessionManager";

const Dashboard = ({ onNavigate }) => {
  const [stats, setStats] = useState({
    totalCalls: 0,
    emergentCalls: 0,
    criticalCalls: 0,
    moderateCalls: 0,
    lowRiskCalls: 0,
  });
  const [recentCalls, setRecentCalls] = useState([]);

  useEffect(() => {
    const loadStats = () => {
      const sessionStats = getSessionStats();
      setStats(sessionStats);

      const history = getAnalysisHistory();
      setRecentCalls(history.slice(0, 5));
    };

    loadStats();
    const interval = setInterval(loadStats, 2000);
    return () => clearInterval(interval);
  }, []);

  // --- Helper: Map Triage to UI Colors ---
  const getTriageUI = (level) => {
    const l = level?.toLowerCase();
    switch (l) {
      case "emergent":
        return "text-red-600 bg-red-50 border-red-200";
      case "urgent":
        return "text-orange-600 bg-orange-50 border-orange-200";
      case "review":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "monitor":
        return "text-emerald-600 bg-emerald-50 border-emerald-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const formatTimestamp = (isoString) => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins} min ago`;
    return `${Math.floor(diffMins / 60)} hours ago`;
  };

  const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
  const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <div className="flex items-center justify-between">
        <motion.h1 variants={item} className="text-2xl font-bold text-foreground">
          Dashboard Overview
        </motion.h1>
        <motion.button
          variants={item}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onNavigate("call-analysis")}
          style={{ background: 'linear-gradient(to right, #166E39, #287D49)' }}
          className="px-4 py-2 text-white rounded-lg hover:shadow-lg transition-all font-medium flex items-center space-x-2"
        >
          <span>Analyze New Call</span>
          <ArrowRight size={16} />
        </motion.button>
      </div>

      {/* Session Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        {[
          { label: "Calls Analyzed", value: stats.totalCalls, icon: FileAudio, color: "bg-emerald-50 text-emerald-600" },
          { label: "Emergent AE", value: stats.criticalCalls, icon: AlertTriangle, color: "bg-red-50 text-red-600" },
          { label: "Urgent AE", value: stats.criticalCalls, icon: AlertCircle, color: "bg-orange-50 text-orange-600" },
          { label: "Need Review", value: stats.moderateCalls, icon: FileText, color: "bg-yellow-50 text-yellow-600" },
          { label: "Monitor", value: stats.lowRiskCalls, icon: FileText, color: "bg-green-50 text-green-600" },
        ].map((stat, i) => (
          <motion.div key={i} variants={item} className="bg-card/50 backdrop-blur-sm p-6 rounded-xl border border-border shadow-sm">
            <div className={`p-3 rounded-lg w-fit mb-4 ${stat.color}`}>
              <stat.icon size={24} />
            </div>
            <h3 className="text-2xl font-bold text-foreground">{stat.value}</h3>
            <p className="text-sm text-muted-foreground">{stat.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Recent Analyses */}
      <motion.div variants={item} className="bg-card/50 backdrop-blur-sm rounded-xl border border-border shadow-sm overflow-hidden">
        <div className="p-6 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">Recent Analysis</h2>
          <button onClick={() => onNavigate("history")} style={{ color: '#166E39' }} className="text-sm font-medium hover:underline">
            View All
          </button>
        </div>

        {recentCalls.length === 0 ? (
          <div className="p-12 text-center">
            <FileAudio size={48} className="mx-auto text-muted-foreground opacity-20 mb-4" />
            <p className="text-muted-foreground mb-4">No calls analyzed yet this session</p>
            <button onClick={() => onNavigate("call-analysis")} style={{ backgroundColor: '#166E39' }} className="px-4 py-2 text-white rounded-lg">
              Analyze Your First Call
            </button>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {recentCalls.map((call) => {
              // --- Logic to extract Adverse Event name and Triage level ---
              const primaryAE = call.summary?.suspected_adverse_events?.[0]?.event_meddra_pt || "No Event Detected";
              const triageLevel = call.summary?.triage || "Monitor";

              return (
                <div
                  key={call.id}
                  onClick={() => onNavigate("call-analysis", call)}
                  className="p-4 hover:bg-accent/50 transition-colors flex items-center justify-between group cursor-pointer"
                >
                  <div className="flex items-center space-x-4 flex-1 min-w-0">
                    <div className="p-2 rounded-lg flex-shrink-0" style={{ backgroundColor: 'rgba(22, 110, 57, 0.1)' }}>
                      <FileAudio size={20} style={{ color: '#166E39' }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-foreground truncate">{call.fileName}</h4>
                      <div className="flex items-center text-xs text-muted-foreground mt-1">
                        <Clock size={12} className="mr-1" />
                        {formatTimestamp(call.timestamp)}
                      </div>
                    </div>
                  </div>

                  {/* Prediction Column: Shows the AE name and the Triage Badge */}
                  <div className="flex items-center space-x-6 flex-shrink-0">
                    <div className="text-right">
                      <div className="text-sm font-bold text-foreground uppercase tracking-tight">
                        {primaryAE}
                      </div>
                      <div className={`text-[10px] px-2 py-0.5 rounded-full border inline-block mt-1 font-bold uppercase ${getTriageUI(triageLevel)}`}>
                        {triageLevel}
                      </div>
                    </div>
                    <ChevronRight size={18} className="text-muted-foreground group-hover:text-emerald-600 transition-colors" />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;