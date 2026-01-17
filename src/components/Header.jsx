// import React from "react";
// import { Activity } from "lucide-react";

// const Header = () => {
//   return (
//     <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
//       <div className="flex items-center space-x-3">
//         <div className="w-10 h-10 bg-gradient-to-br from-primary to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-primary/20">
//           <Activity className="w-6 h-6 text-white" />
//         </div>
//         <div>
//           <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-600">
//             AE_WATCH AI
//           </h1>
//           <p className="text-xs text-muted-foreground">
//             Clinical Safety Assistant
//           </p>
//         </div>
//       </div>

//       <div className="text-sm text-muted-foreground">
//         <span className="font-medium">Session Active</span>
//       </div>
//     </header>
//   );
// };

// export default Header;

import React from "react";
import { Leaf } from "lucide-react";

const Header = () => {
  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center space-x-3">
        {/* Logo Icon with new Green Gradient */}
        <div 
          style={{ background: 'linear-gradient(to bottom right, #166E39, #1E5C1A)' }}
          className="w-10 h-10 rounded-lg flex items-center justify-center shadow-lg shadow-green-900/20"
        >
          <Leaf className="w-6 h-6 text-white" />
        </div>
        
        <div>
          {/* Brand Title with Gradient Text */}
          <h1 
            style={{ 
              backgroundImage: 'linear-gradient(to right, #166E39, #287D49)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
            className="text-lg font-bold"
          >
            AE_WATCH AI
          </h1>
          <p className="text-xs text-muted-foreground">
            Clinical Safety Assistant
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2 text-sm text-muted-foreground">
        {/* Pulsing Green Indicator */}
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        <span className="font-medium">Session Active</span>
      </div>
    </header>
  );
};

export default Header;