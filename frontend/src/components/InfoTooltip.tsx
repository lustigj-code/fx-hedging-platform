import React, { useState } from 'react';
import { HelpCircle, Info, AlertTriangle } from 'lucide-react';

type InfoTooltipProps = {
  term: string;
  shortExplanation: string;
  detailedExplanation?: string;
  example?: string;
  learnMoreLink?: string;
  icon?: 'info' | 'help' | 'warning';
};

const InfoTooltip: React.FC<InfoTooltipProps> = ({
  term,
  shortExplanation,
  detailedExplanation,
  example,
  learnMoreLink,
  icon = 'help',
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const IconComponent =
    icon === 'info' ? Info : icon === 'warning' ? AlertTriangle : HelpCircle;

  return (
    <div className="inline-block relative ml-1">
      {/* Trigger Icon */}
      <button
        type="button"
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center justify-center w-4 h-4 text-gray-500 hover:text-white transition-colors cursor-help"
        aria-label={`More info about ${term}`}
      >
        <IconComponent className="w-4 h-4" />
      </button>

      {/* Tooltip Popup */}
      {isOpen && (
        <div className="absolute z-50 w-80 p-4 bg-gray-900 border border-gray-700 rounded-lg shadow-xl left-0 top-6">
          {/* Term Header */}
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-bold text-white">{term}</h4>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-500 hover:text-white text-xs"
            >
              ✕
            </button>
          </div>

          {/* Short Explanation */}
          <p className="text-sm text-gray-300 mb-3">{shortExplanation}</p>

          {/* Detailed Explanation */}
          {detailedExplanation && (
            <p className="text-xs text-gray-400 mb-3">{detailedExplanation}</p>
          )}

          {/* Example */}
          {example && (
            <div className="bg-black border border-gray-800 rounded p-2 mb-3">
              <p className="text-xs text-gray-300">
                <span className="font-semibold text-white">Example:</span> {example}
              </p>
            </div>
          )}

          {/* Learn More Link */}
          {learnMoreLink && (
            <a
              href={learnMoreLink}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-gray-500 hover:text-white underline"
            >
              Learn more →
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default InfoTooltip;
