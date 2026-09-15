import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';

// Collector (Kept in primary mobile bundle)
import { CollectorLayout } from '../features/collector/CollectorLayout';
import { Home } from '../features/collector/Home';
import { Basket } from '../features/collector/Basket';
import { LotBuilder } from '../features/collector/LotBuilder';
import { LotsListView } from '../features/collector/LotsListView';
import { LotDetail } from '../features/collector/LotDetail';
import { FindBuyers } from '../features/collector/FindBuyers';
import { TrackingView } from '../features/collector/TrackingView';
import { HandoverView } from '../features/collector/HandoverView';
import { PaymentSuccess } from '../features/collector/PaymentSuccess';
import { PricesView } from '../features/collector/PricesView';
import { WalletView } from '../features/collector/WalletView';
import { SafetyHub } from '../features/collector/SafetyHub';
import { SupportHub } from '../features/collector/SupportHub';
import { TicketChat } from '../features/collector/TicketChat';
import { NotificationsView } from '../features/collector/NotificationsView';

// Helper for lazy loading named exports
const lazyNamed = <T extends React.ComponentType<any>>(
  importer: () => Promise<{ [key: string]: any }>,
  exportName: string
) => React.lazy(() => importer().then((mod) => ({ default: mod[exportName] as T })));

// Recycler (Lazy loaded console bundle)
const RecyclerLayout = lazyNamed(() => import('../features/recycler/RecyclerLayout'), 'RecyclerLayout');
const RecyclerOverview = lazyNamed(() => import('../features/recycler/RecyclerOverview'), 'RecyclerOverview');
const RecyclerMarketplace = lazyNamed(() => import('../features/recycler/RecyclerMarketplace'), 'RecyclerMarketplace');
const RecyclerHandovers = lazyNamed(() => import('../features/recycler/RecyclerHandovers'), 'RecyclerHandovers');
const RecyclerInventory = lazyNamed(() => import('../features/recycler/RecyclerInventory'), 'RecyclerInventory');
const RecyclerCompliance = lazyNamed(() => import('../features/recycler/RecyclerCompliance'), 'RecyclerCompliance');
const RecyclerPrices = lazyNamed(() => import('../features/recycler/RecyclerPrices'), 'RecyclerPrices');
const HandoverDesk = lazyNamed(() => import('../features/recycler/HandoverDesk'), 'HandoverDesk');

// Aggregator (Lazy loaded console bundle)
const AggregatorDashboard = lazyNamed(() => import('../features/aggregator/AggregatorDashboard'), 'AggregatorDashboard');

// Admin (Lazy loaded console bundle)
const AdminLayout = lazyNamed(() => import('../features/admin/AdminLayout'), 'AdminLayout');
const AdminDashboard = lazyNamed(() => import('../features/admin/AdminDashboard'), 'AdminDashboard');
const TraceabilityExplorer = lazyNamed(() => import('../features/admin/TraceabilityExplorer'), 'TraceabilityExplorer');
const AdminSupportQueue = lazyNamed(() => import('../features/admin/AdminSupportQueue'), 'AdminSupportQueue');
const AdminCompliance = lazyNamed(() => import('../features/admin/AdminCompliance'), 'AdminCompliance');
const Collector360 = lazyNamed(() => import('../features/admin/Collector360'), 'Collector360');
const DataHealthPanel = lazyNamed(() => import('../features/admin/DataHealthPanel'), 'DataHealthPanel');
const UnitEconomics = lazyNamed(() => import('../features/admin/UnitEconomics'), 'UnitEconomics');
// AI Console pages
const AIOverview = lazyNamed(() => import('../features/admin/AIOverview'), 'default');
const ClassifierPanel = lazyNamed(() => import('../features/admin/ClassifierPanel'), 'default');
const LabelReviewQueue = lazyNamed(() => import('../features/admin/LabelReviewQueue'), 'default');
const PredictionsLog = lazyNamed(() => import('../features/admin/PredictionsLog'), 'default');
const ValuationPanel = lazyNamed(() => import('../features/admin/ValuationPanel'), 'default');
const MatchingWeightsEditor = lazyNamed(() => import('../features/admin/MatchingWeightsEditor'), 'default');
const DriftPanel = lazyNamed(() => import('../features/admin/DriftPanel'), 'default');

// Public & Auth
const PublicVerifyView = lazyNamed(() => import('../features/verify/PublicVerifyView'), 'PublicVerifyView');
import { LoginView } from '../features/auth/LoginView';

const Lazy = ({ component: Component }: { component: React.ComponentType }) => (
  <React.Suspense fallback={<div className="p-8 text-center text-xs text-[#5B6B62]">Loading console...</div>}>
    <Component />
  </React.Suspense>
);

export const router = createBrowserRouter([
  // Collector Flow
  {
    path: '/',
    element: <CollectorLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'basket', element: <Basket /> },
      { path: 'build-lot', element: <LotBuilder /> },
      { path: 'add-scrap', element: <LotBuilder /> },
      { path: 'lots', element: <LotsListView /> },
      { path: 'lots/:lotId', element: <LotDetail /> },
      { path: 'lots/:lotId/buyers', element: <FindBuyers /> },
      { path: 'lots/:lotId/track', element: <TrackingView /> },
      { path: 'lots/:lotId/handover', element: <HandoverView /> },
      { path: 'handover/:id', element: <HandoverView /> },
      { path: 'lots/:lotId/success', element: <PaymentSuccess /> },
      { path: 'prices', element: <PricesView /> },
      { path: 'wallet', element: <WalletView /> },
      { path: 'safety', element: <SafetyHub /> },
      { path: 'support', element: <SupportHub /> },
      { path: 'support/:ticketId', element: <TicketChat /> },
      { path: 'notifications', element: <NotificationsView /> },
    ],
  },

  // Recycler Flow
  {
    path: '/recycler',
    element: <Lazy component={RecyclerLayout} />,
    children: [
      { index: true, element: <Lazy component={RecyclerOverview} /> },
      { path: 'marketplace', element: <Lazy component={RecyclerMarketplace} /> },
      { path: 'handovers', element: <Lazy component={RecyclerHandovers} /> },
      { path: 'inventory', element: <Lazy component={RecyclerInventory} /> },
      { path: 'compliance', element: <Lazy component={RecyclerCompliance} /> },
      { path: 'prices', element: <Lazy component={RecyclerPrices} /> },
      { path: 'handover-desk', element: <Lazy component={HandoverDesk} /> },
    ],
  },

  // Direct Mobile Handover Desk route (Weighbridge Chrome PWA)
  {
    path: '/handover-desk',
    element: <Lazy component={HandoverDesk} />,
  },

  // Aggregator Flow
  {
    path: '/aggregator',
    element: <Lazy component={AggregatorDashboard} />,
  },

  {
    path: '/admin',
    element: <Lazy component={AdminLayout} />,
    children: [
      { index: true, element: <Lazy component={AdminDashboard} /> },
      { path: 'data-health', element: <Lazy component={DataHealthPanel} /> },
      { path: 'unit-economics', element: <Lazy component={UnitEconomics} /> },
      { path: 'trace', element: <Lazy component={TraceabilityExplorer} /> },
      { path: 'support', element: <Lazy component={AdminSupportQueue} /> },
      { path: 'compliance', element: <Lazy component={AdminCompliance} /> },
      { path: 'collectors', element: <Lazy component={Collector360} /> },
      // AI Console routes
      { path: 'ai', element: <Lazy component={AIOverview} /> },
      { path: 'ai/classifier', element: <Lazy component={ClassifierPanel} /> },
      { path: 'ai/labels', element: <Lazy component={LabelReviewQueue} /> },
      { path: 'ai/predictions', element: <Lazy component={PredictionsLog} /> },
      { path: 'ai/valuation', element: <Lazy component={ValuationPanel} /> },
      { path: 'ai/weights', element: <Lazy component={MatchingWeightsEditor} /> },
      { path: 'ai/drift', element: <Lazy component={DriftPanel} /> },
    ],
  },

  // Direct Unit Economics access
  {
    path: '/unit-economics',
    element: <Lazy component={UnitEconomics} />,
  },

  // Public Document Verification (Form 6 Manifest & Cert)
  {
    path: '/verify/:docNumber',
    element: <Lazy component={PublicVerifyView} />,
  },
  {
    path: '/verify',
    element: <Lazy component={PublicVerifyView} />,
  },

  // Authentication
  {
    path: '/login',
    element: <LoginView defaultTab="login" />,
  },
  {
    path: '/signup',
    element: <LoginView defaultTab="signup" />,
  },

  // Fallback
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
