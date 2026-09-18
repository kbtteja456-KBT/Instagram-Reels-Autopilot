import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { CircuitStormCanvas } from './components/CircuitStormCanvas';
import { DashboardPage } from './pages/DashboardPage';
import { VideosPage } from './pages/VideosPage';
import { ProvidersPage } from './pages/ProvidersPage';
import { StylePage } from './pages/StylePage';
import { SettingsPage } from './pages/SettingsPage';
import { LandingPage } from './pages/LandingPage';
import { AuthPage } from './pages/AuthPage';
import { PrivacyPage } from './pages/PrivacyPage';
import { TermsPage } from './pages/TermsPage';
import { ApiKeyVaultModal } from './components/ApiKeyVaultModal';
import { CreateVideoModal } from './components/CreateVideoModal';
import {
  api,
  getToken,
  UserProfile,
  WorkspaceContext,
  InstagramAccount,
  Reel,
  AutopilotStatus,
  ProvidersHealthResponse
} from './services/api';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(() => {
    // Default active session for instant local evaluation
    return {
      id: 'usr_default_01',
      email: 'creator@instagram-reels.local',
      full_name: 'Reels Creator Pro',
      role: 'owner',
      is_owner: true,
      trial_quota: { videos_generated: 2, max_videos: 10 }
    };
  });
  const [currentWorkspace, setCurrentWorkspace] = useState<WorkspaceContext | null>({
    id: 'ws_default',
    name: "Reels Creator Pro's Workspace",
    niche: 'AI & Modern Technology',
    is_legacy_default: true
  });
  const [isAuthChecking, setIsAuthChecking] = useState<boolean>(false);
  const [isVaultOpen, setIsVaultOpen] = useState<boolean>(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState<boolean>(false);

  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [autopilotStatus, setAutopilotStatus] = useState<AutopilotStatus | null>(null);
  const [providersHealth, setProvidersHealth] = useState<ProvidersHealthResponse | null>(null);
  const [account, setAccount] = useState<InstagramAccount | null>(null);
  const [reels, setReels] = useState<Reel[]>([]);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const [publicView, setPublicView] = useState<'app' | 'landing' | 'auth' | 'privacy' | 'terms'>(() => {
    if (typeof window !== 'undefined') {
      if (window.location.pathname === '/privacy') return 'privacy';
      if (window.location.pathname === '/terms') return 'terms';
      if (window.location.pathname === '/landing') return 'landing';
    }
    return 'app';
  });

  useEffect(() => {
    const handlePopState = () => {
      if (window.location.pathname === '/privacy') setPublicView('privacy');
      else if (window.location.pathname === '/terms') setPublicView('terms');
      else if (window.location.pathname === '/landing') setPublicView('landing');
      else setPublicView('app');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigateTo = (view: 'app' | 'landing' | 'auth' | 'privacy' | 'terms') => {
    setPublicView(view);
    const path = view === 'privacy' ? '/privacy' : view === 'terms' ? '/terms' : view === 'landing' ? '/landing' : '/';
    window.history.pushState({}, '', path);
  };

  useEffect(() => {
    checkSession();
    loadAllData();
  }, []);

  const checkSession = async () => {
    const token = getToken();
    if (!token) return;
    try {
      const me = await api.getMe();
      setCurrentUser(me.user);
      setCurrentWorkspace(me.workspace);
    } catch (e) {
      console.warn('Session verification note:', e);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      if (!document.hidden) {
        loadAllData();
      }
    }, 12000);

    const handleVisibilityChange = () => {
      if (!document.hidden) {
        loadAllData();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  const loadAllData = async () => {
    try {
      const [accRes, vidsRes, autoRes, healthRes] = await Promise.all([
        api.instagram.getAccount().catch(() => null),
        api.videos.list().catch(() => []),
        api.autopilot.getStatus().catch(() => null),
        api.providers.getHealth().catch(() => null)
      ]);
      if (accRes && accRes.account) setAccount(accRes.account);
      if (vidsRes) setReels(vidsRes);
      if (autoRes) setAutopilotStatus(autoRes);
      if (healthRes) setProvidersHealth(healthRes);
    } catch (e) {
      console.error('Data poll error:', e);
    }
  };

  const handleAuthenticated = (user: UserProfile, workspace: WorkspaceContext) => {
    setCurrentUser(user);
    setCurrentWorkspace(workspace);
    setPublicView('app');
    loadAllData();
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
    setCurrentWorkspace(null);
    setPublicView('landing');
  };

  const handleToggleAutopilot = async () => {
    try {
      await api.autopilot.toggle();
      await loadAllData();
    } catch (e) {
      console.error('Failed to toggle autopilot:', e);
    }
  };

  const handleTriggerSlot = async (slotIndex: number) => {
    try {
      await api.autopilot.triggerSlot(slotIndex);
      await loadAllData();
      alert(`Slot ${slotIndex} pipeline launched! Follow progress in the live telemetry feed.`);
    } catch (e) {
      alert('Failed to trigger slot: ' + e);
    }
  };

  const handleCreateSubmit = async (params: any) => {
    setIsGenerating(true);
    try {
      await api.videos.generate(params);
      await loadAllData();
      setActiveTab('videos');
    } catch (e: any) {
      alert('Failed to generate Reel: ' + e.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePublishReel = async (reelId: string) => {
    try {
      const res = await api.videos.publish(reelId);
      alert(`🎉 Reel published successfully! URL: ${res.instagram_url}`);
      await loadAllData();
    } catch (err: any) {
      alert('Failed to publish Reel: ' + err.message);
    }
  };

  const handleDeleteReel = async (reelId: string) => {
    try {
      await api.videos.delete(reelId);
      setReels((prev) => prev.filter((v) => (v._id !== reelId && v.id !== reelId)));
    } catch (e) {
      console.error(e);
    }
  };

  const handleDisconnectInstagram = async () => {
    if (confirm('Are you sure you want to disconnect your Instagram account? This purges all encrypted tokens.')) {
      await api.instagram.disconnect();
      await loadAllData();
    }
  };

  // Public views
  if (publicView === 'privacy') {
    return (
      <div className="app-container" style={{ position: 'relative', width: '100%', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', overflowX: 'hidden', overflowY: 'auto' }}>
        <CircuitStormCanvas />
        <PrivacyPage onBack={() => navigateTo(currentUser ? 'app' : 'landing')} />
      </div>
    );
  }

  if (publicView === 'terms') {
    return (
      <div className="app-container" style={{ position: 'relative', width: '100%', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', overflowX: 'hidden', overflowY: 'auto' }}>
        <CircuitStormCanvas />
        <TermsPage onBack={() => navigateTo(currentUser ? 'app' : 'landing')} />
      </div>
    );
  }

  if (publicView === 'landing' || (!currentUser && !isAuthChecking && publicView !== 'auth')) {
    return (
      <div className="app-container" style={{ position: 'relative', width: '100%', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', overflowX: 'hidden', overflowY: 'auto' }}>
        <CircuitStormCanvas />
        <LandingPage
          onLoginClick={() => navigateTo('auth')}
          onPrivacyClick={() => navigateTo('privacy')}
          onTermsClick={() => navigateTo('terms')}
        />
      </div>
    );
  }

  if (publicView === 'auth') {
    return (
      <div className="app-container" style={{ position: 'relative', width: '100%', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', overflowX: 'hidden', overflowY: 'auto' }}>
        <CircuitStormCanvas />
        <AuthPage
          onAuthenticated={handleAuthenticated}
          onBack={() => navigateTo('landing')}
        />
      </div>
    );
  }

  const renderActivePage = () => {
    switch (activeTab) {
      case 'videos':
        return (
          <VideosPage
            reels={reels}
            onGenerateClick={() => setIsCreateModalOpen(true)}
            onPublishReel={handlePublishReel}
            onDeleteReel={handleDeleteReel}
          />
        );
      case 'providers':
        return <ProvidersPage healthData={providersHealth} onRefresh={loadAllData} />;
      case 'style':
        return <StylePage />;
      case 'settings':
        return <SettingsPage onDisconnectInstagram={handleDisconnectInstagram} />;
      case 'privacy':
        return <PrivacyPage onBack={() => setActiveTab('dashboard')} />;
      case 'terms':
        return <TermsPage onBack={() => setActiveTab('dashboard')} />;
      case 'dashboard':
      default:
        return (
          <DashboardPage
            account={account || undefined}
            reels={reels}
            autopilotStatus={autopilotStatus || undefined}
            onToggleAutopilot={handleToggleAutopilot}
            onGenerateClick={() => setIsCreateModalOpen(true)}
            onRefreshData={loadAllData}
          />
        );
    }
  };

  const getPageTitle = () => {
    switch (activeTab) {
      case 'videos': return 'Reels Library';
      case 'providers': return 'Provider Health';
      case 'style': return 'Style Analyzer';
      case 'settings': return 'Instagram & System Settings';
      case 'privacy': return 'Privacy Policy';
      case 'terms': return 'Terms of Service';
      default: return 'Autopilot Dashboard';
    }
  };

  return (
    <div className="app-container">
      {/* 3D Dynamic Circuit Canvas Background */}
      <CircuitStormCanvas />

      {/* Luxury Sticky Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isOwner={currentUser?.is_owner ?? true}
        onOpenVault={() => setIsVaultOpen(true)}
      />

      {/* Main Content Pane */}
      <div className="main-content">
        <Header
          title={getPageTitle()}
          zeroCostMode={autopilotStatus?.zero_cost_mode ?? true}
          channelTitle={account?.username || currentWorkspace?.name}
          channelAvatar={account?.profile_picture_url}
          isGenerating={isGenerating}
          onGenerateClick={() => setIsCreateModalOpen(true)}
          onOpenVault={() => setIsVaultOpen(true)}
          trialVideosUsed={currentUser?.trial_quota?.videos_generated ?? 1}
          trialMaxVideos={currentUser?.trial_quota?.max_videos ?? 10}
          isLegacyOwner={true}
          onLogout={handleLogout}
        />
        {renderActivePage()}
      </div>

      {/* BYOK API Key Vault Modal */}
      <ApiKeyVaultModal
        isOpen={isVaultOpen}
        onClose={() => setIsVaultOpen(false)}
        onKeysUpdated={loadAllData}
      />

      {/* Manual Reel Creation & Render Modal */}
      <CreateVideoModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateSubmit}
      />
    </div>
  );
};

export default App;
