import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { marked } from 'marked';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  // ============================================================
  // API
  // ============================================================

  private apiUrl = 'http://localhost:8000';


  // ============================================================
  // GLOBAL
  // ============================================================

  errorMessage: string = '';
  successMessage: string = '';


  // ============================================================
  // MARKDOWN
  // ============================================================

  renderMarkdown(markdown: string): string {

    if (!markdown) {
      return '';
    }

    return marked.parse(markdown) as string;
  }


  // ============================================================
  // WORKFLOW STEPS
  // ============================================================

  readonly workflowSteps = [

    {
      id: 1,
      title: 'Jira Agent',
      shortTitle: 'Ticket',
      icon: '🔎'
    },

    {
      id: 2,
      title: 'Analysis Agent',
      shortTitle: 'Analyse',
      icon: '🧠'
    },

    {
      id: 3,
      title: 'Prompt Agent',
      shortTitle: 'Prompt',
      icon: '📝'
    },

    {
      id: 4,
      title: 'Git Agent',
      shortTitle: 'Git',
      icon: '🔀'
    },

    {
      id: 5,
      title: 'OpenCode',
      shortTitle: 'Execution',
      icon: '🚀'
    },

    {
      id: 6,
      title: 'Git Deploy',
      shortTitle: 'Deploy',
      icon: '📤'
    }

  ];

  get visibleWorkflowSteps(): any[] {
    return this.workflowSteps.filter(step => step.id !== 4);
  }


  // ============================================================
  // ORCHESTRATOR
  // ============================================================

  orchestratorIssueKey: string = '';

  orchestratorRepositoryUrl: string = '';

  orchestrating: boolean = false;

  orchestratorStarted: boolean = false;

  orchestratorStep: number = 0;

  orchestratorTicket: any = null;

  orchestratorSubtasks: any[] = [];

  orchestratorComplexity: string = '';

  orchestratorAnalysis: string = '';

  orchestratorPrompt: string = '';

  orchestratorGitResult: any = null;

  orchestratorResult: string = '';

  orchestratorSuccess: boolean = false;

  orchestratorFailed: boolean = false;

  orchestratorFailedStep: number = 0;

  orchestratorEditing: boolean = false;


  // ============================================================
  // ORCHESTRATOR DEPLOY
  // ============================================================

  orchestratorDeployResult: any = null;

  orchestratorDeployed: boolean = false;


  // ============================================================
  // STEP BY STEP
  // ============================================================

  stepIssueKey: string = '';

  stepRepositoryUrl: string = '';

  stepLoading: boolean = false;

  stepTicket: any = null;

  stepAnalysis: string = '';

  stepPrompt: string = '';

  stepGitResult: any = null;

  stepResult: string = '';

  stepSuccess: boolean = false;

  stepFailed: boolean = false;

  stepFailedStep: number = 0;


  // ============================================================
  // STEP BY STEP DEPLOY
  // ============================================================

  stepDeployResult: any = null;

  stepDeployed: boolean = false;


  // ============================================================
  // EDIT MODES
  // ============================================================

  stepTicketEditing: boolean = false;

  stepAnalysisEditing: boolean = false;

  stepPromptEditing: boolean = false;


  // ============================================================
  // BACKUPS
  // ============================================================

  private stepTicketBackup: any = null;

  private stepAnalysisBackup: string = '';

  private stepPromptBackup: string = '';


  // ============================================================
  // CONSTRUCTOR
  // ============================================================

  constructor(
    private http: HttpClient
  ) {}


  // ============================================================
  // ERROR
  // ============================================================

  clearError(): void {
    this.errorMessage = '';
  }


  // ============================================================
  // SUCCESS
  // ============================================================

  clearSuccess(): void {
    this.successMessage = '';
  }


  // ============================================================
  // API ERROR HELPER
  // ============================================================

  private getApiErrorMessage(
    error: any,
    fallback: string
  ): string {

    const apiError = error?.error;

    if (!apiError) {
      return fallback;
    }


    // ==========================================================
    // FastAPI :
    //
    // {
    //   "detail": "..."
    // }
    // ==========================================================

    if (
      typeof apiError.detail === 'string' &&
      apiError.detail.trim()
    ) {

      return apiError.detail;
    }


    // ==========================================================
    // FastAPI 422 :
    //
    // {
    //   "detail": [
    //     {
    //       "loc": [...],
    //       "msg": "...",
    //       "type": "..."
    //     }
    //   ]
    // }
    // ==========================================================

    if (
      Array.isArray(apiError.detail) &&
      apiError.detail.length > 0
    ) {

      return apiError.detail
        .map((item: any) => {

          const location =
            Array.isArray(item?.loc)
              ? item.loc.join(' → ')
              : '';

          const message =
            item?.msg ||
            'Erreur de validation';

          return location
            ? `${location}: ${message}`
            : message;

        })
        .join(' | ');
    }


    // ==========================================================
    // Generic message
    // ==========================================================

    if (
      typeof apiError.message === 'string' &&
      apiError.message.trim()
    ) {

      return apiError.message;
    }


    return fallback;
  }


  // ============================================================
  // VALIDATE JIRA ISSUE KEY
  // ============================================================

  private normalizeIssueKey(value: string): string {

    return (value || '')
      .trim()
      .toUpperCase();
  }


  // ============================================================
  // VALIDATE GITHUB URL
  // ============================================================

  private normalizeGithubUrl(value: string): string {

    return (value || '').trim();
  }


  // ============================================================
  // ORCHESTRATOR STATUS
  // ============================================================

  getOrchestratorStepStatus(stepId: number): string {

    if (
      this.orchestratorFailed &&
      this.orchestratorFailedStep === stepId
    ) {

      return 'failed';
    }


    if (
      this.orchestratorSuccess &&
      this.orchestratorStep >= stepId
    ) {

      return 'completed';
    }


    if (
      this.orchestratorStep > stepId
    ) {

      return 'completed';
    }


    if (
      this.orchestratorStep === stepId &&
      this.orchestrating
    ) {

      return 'running';
    }


    if (
      this.orchestratorStep === stepId &&
      !this.orchestrating &&
      stepId <= 3 &&
      (
        this.orchestratorTicket ||
        this.orchestratorAnalysis ||
        this.orchestratorPrompt
      )
    ) {

      return 'completed';
    }


    return 'idle';
  }


  getOrchestratorStatusLabel(stepId: number): string {

    const status =
      this.getOrchestratorStepStatus(stepId);

    switch (status) {

      case 'running':
        return 'En cours';

      case 'completed':
        return 'Terminé';

      case 'failed':
        return 'Échec';

      default:
        return 'En attente';
    }
  }


  isOrchestratorStepCompleted(stepId: number): boolean {
    return this.getOrchestratorStepStatus(stepId) === 'completed';
  }


  isOrchestratorStepRunning(stepId: number): boolean {
    return this.getOrchestratorStepStatus(stepId) === 'running';
  }


  isOrchestratorStepFailed(stepId: number): boolean {
    return this.getOrchestratorStepStatus(stepId) === 'failed';
  }


  // ============================================================
  // STEP BY STEP STATUS
  // ============================================================

  getStepByStepStatus(stepId: number): string {

    if (
      this.stepFailed &&
      this.stepFailedStep === stepId
    ) {

      return 'failed';
    }


    if (stepId === 1) {

      if (this.stepTicket) {
        return 'completed';
      }

      if (this.stepLoading) {
        return 'running';
      }

      return 'idle';
    }


    if (stepId === 2) {

      if (this.stepAnalysis) {
        return 'completed';
      }

      if (
        this.stepLoading &&
        this.stepTicket
      ) {

        return 'running';
      }

      return 'idle';
    }


    if (stepId === 3) {

      if (this.stepPrompt) {
        return 'completed';
      }

      if (
        this.stepLoading &&
        this.stepAnalysis
      ) {

        return 'running';
      }

      return 'idle';
    }


    if (stepId === 4) {

      if (
        this.stepGitResult &&
        this.stepGitResult.success === true
      ) {

        return 'completed';
      }

      if (
        this.stepLoading &&
        this.stepPrompt
      ) {

        return 'running';
      }

      return 'idle';
    }


    if (stepId === 5) {

      if (
        this.stepResult &&
        this.stepSuccess
      ) {

        return 'completed';
      }

      if (
        this.stepLoading &&
        this.stepPrompt &&
        this.stepGitResult &&
        !this.stepResult
      ) {

        return 'running';
      }

      return 'idle';
    }


    if (stepId === 6) {

      if (this.stepDeployed) {
        return 'completed';
      }

      if (
        this.stepLoading &&
        this.stepResult
      ) {

        return 'running';
      }

      return 'idle';
    }


    return 'idle';
  }


  getStepByStepStatusLabel(stepId: number): string {

    const status =
      this.getStepByStepStatus(stepId);

    switch (status) {

      case 'running':
        return 'En cours';

      case 'completed':
        return 'Terminé';

      case 'failed':
        return 'Échec';

      default:
        return 'En attente';
    }
  }


  isStepCompleted(stepId: number): boolean {
    return this.getStepByStepStatus(stepId) === 'completed';
  }


  isStepRunning(stepId: number): boolean {
    return this.getStepByStepStatus(stepId) === 'running';
  }


  isStepFailed(stepId: number): boolean {
    return this.getStepByStepStatus(stepId) === 'failed';
  }


  // ============================================================
  // ORCHESTRATOR - WORKFLOW
  // ============================================================

  runOrchestrator(): void {

    // ==========================================================
    // IMPORTANT :
    //
    // Cette variable doit TOUJOURS être la clé Jira.
    //
    // Exemple :
    // KAN-1
    //
    // JAMAIS :
    // https://github.com/...
    // ==========================================================

    const key =
      this.normalizeIssueKey(
        this.orchestratorIssueKey
      );


    console.log(
      '============================================'
    );

    console.log(
      '🚀 ORCHESTRATOR START'
    );

    console.log(
      '🎯 Jira Issue Key:',
      key
    );

    console.log(
      '============================================'
    );


    if (!key) {

      this.errorMessage =
        'Veuillez entrer une clé Jira, par exemple KAN-1.';

      return;
    }


    // ==========================================================
    // PROTECTION CONTRE L'ERREUR 404
    //
    // On refuse explicitement une URL GitHub comme issue key.
    // ==========================================================

    if (
      key.includes('HTTP://') ||
      key.includes('HTTPS://') ||
      key.includes('GITHUB.COM')
    ) {

      this.errorMessage =
        'Erreur : le champ Jira Ticket contient une URL GitHub. Veuillez mettre KAN-1 dans Jira Ticket et l’URL GitHub dans Repository.';

      console.error(
        '❌ ISSUE KEY INVALIDE:',
        key
      );

      return;
    }


    this.orchestratorIssueKey = key;

    this.orchestrating = true;

    this.orchestratorStarted = true;

    this.orchestratorStep = 1;

    this.orchestratorTicket = null;

    this.orchestratorSubtasks = [];

    this.orchestratorComplexity = '';

    this.orchestratorAnalysis = '';

    this.orchestratorPrompt = '';

    this.orchestratorGitResult = null;

    this.orchestratorResult = '';

    this.orchestratorDeployResult = null;

    this.orchestratorDeployed = false;

    this.orchestratorSuccess = false;

    this.orchestratorFailed = false;

    this.orchestratorFailedStep = 0;

    this.orchestratorEditing = false;

    this.errorMessage = '';

    this.successMessage = '';


    // ==========================================================
    // BACKEND WORKFLOW B
    //
    // IMPORTANT :
    //
    // /api/agents/{issue_key}
    //
    // reçoit UNIQUEMENT :
    //
    // KAN-1
    //
    // Jamais l'URL GitHub.
    // ==========================================================

    const url =
      `${this.apiUrl}/api/agents/${encodeURIComponent(key)}`;


    console.log(
      '🎯 ISSUE KEY ENVOYEE AU BACKEND:',
      key
    );

    console.log(
      '🚀 ORCHESTRATOR API:',
      url
    );


    this.http.get<any>(url).subscribe({

      next: (response) => {

        console.log(
          '✅ Orchestrateur Jira terminé:',
          response
        );


        // ======================================================
        // STEP 1 - JIRA
        // ======================================================

        this.orchestratorTicket =
          response.ticket || null;

        this.orchestratorStep = 1;


        this.orchestratorSubtasks =
          response.subtasks || [];

        this.orchestratorComplexity =
          response.complexity || '';


        /*
         * Petit délai visuel pour laisser la map
         * montrer la progression étape par étape.
         */
        setTimeout(() => {

          // ====================================================
          // STEP 2 - ANALYSIS
          // ====================================================

          this.orchestratorAnalysis =
            response.analysis || '';

          this.orchestratorStep = 2;


          setTimeout(() => {

            // ==================================================
            // STEP 3 - PROMPT
            // ==================================================

            this.orchestratorPrompt =
              response.prompt || '';

            this.orchestratorStep = 3;

            if (!this.orchestratorPrompt) {

              this.errorMessage =
                'Le backend a terminé mais aucun prompt n’a été retourné.';
            } else {
              this.prepareOrchestratorGit();
            }

          }, 350);

        }, 350);

      },


      error: (error) => {

        console.error(
          '❌ Erreur Orchestrateur:',
          error
        );


        this.orchestrating = false;

        this.orchestratorStarted = true;

        this.orchestratorFailed = true;

        this.orchestratorFailedStep =
          this.orchestratorStep || 1;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Impossible d’exécuter l’orchestrateur.'
          );
      }

    });
  }


  // ============================================================
  // ORCHESTRATOR PROMPT EDIT
  // ============================================================

  editOrchestratorPrompt(): void {

    if (!this.orchestratorPrompt) {

      this.errorMessage =
        'Aucun prompt disponible à modifier.';

      return;
    }


    this.errorMessage = '';

    this.orchestratorEditing = true;
  }


  ignoreOrchestratorPrompt(): void {

    this.orchestratorEditing = false;

    this.errorMessage = '';
  }


  // ============================================================
  // ORCHESTRATOR GIT
  // ============================================================

  prepareOrchestratorGit(): void {

    const key =
      this.normalizeIssueKey(
        this.orchestratorIssueKey
      );


    console.log(
      '============================================'
    );

    console.log(
      '🔀 ORCHESTRATOR GIT PREPARE'
    );

    console.log(
      '🎯 Jira Issue Key:',
      key
    );

    console.log(
      '============================================'
    );


    if (!key) {

      this.errorMessage =
        'Veuillez entrer une clé Jira.';

      return;
    }


    if (!this.orchestratorPrompt) {

      this.errorMessage =
        'Veuillez d’abord générer le prompt.';

      return;
    }


    this.orchestratorIssueKey = key;

    this.orchestrating = true;

    this.orchestratorStep = 4;

    this.orchestratorGitResult = null;

    this.orchestratorFailed = false;

    this.orchestratorFailedStep = 0;

    this.errorMessage = '';

    this.successMessage = '';


    const body = {

      issue_key: key,

    };


    console.log(
      '📦 BODY /api/git/prepare:',
      body
    );


    this.http.post<any>(

      `${this.apiUrl}/api/git/prepare`,

      body

    ).subscribe({

      next: (response) => {

        console.log(
          '✅ Git orchestrateur:',
          response
        );


        this.orchestratorGitResult =
          response;


        this.orchestrating = false;


        if (
          response?.success !== true
        ) {

          this.orchestratorFailed = true;

          this.orchestratorFailedStep = 4;

          this.errorMessage =
            response?.message ||
            response?.git_error ||
            'La préparation Git a échoué.';

          return;
        }


        this.successMessage =
          response?.message ||
          'Repository Git préparé avec succès.';
      },


      error: (error) => {

        console.error(
          '❌ Erreur Git orchestrateur:',
          error
        );


        this.orchestrating = false;

        this.orchestratorFailed = true;

        this.orchestratorFailedStep = 4;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Impossible de préparer le repository Git.'
          );
      }

    });
  }


  // ============================================================
  // ORCHESTRATOR OPEN CODE
  // ============================================================

  executeOrchestratorPrompt(): void {

    const key =
      this.normalizeIssueKey(
        this.orchestratorIssueKey
      );


    if (!key) {

      this.errorMessage =
        'Veuillez entrer une clé Jira.';

      return;
    }


    if (!this.orchestratorPrompt.trim()) {

      this.errorMessage =
        'Le prompt est vide.';

      return;
    }


    if (!this.orchestratorGitResult) {

      this.errorMessage =
        'Veuillez d’abord préparer le repository Git.';

      return;
    }


    if (
      this.orchestratorGitResult?.success !== true
    ) {

      this.errorMessage =
        'La préparation Git n’a pas réussi.';

      return;
    }


    this.orchestrating = true;

    this.orchestratorStep = 5;

    this.orchestratorResult = '';

    this.orchestratorSuccess = false;

    this.orchestratorFailed = false;

    this.orchestratorFailedStep = 0;

    this.errorMessage = '';


    const body = {

      issue_key: key,

      prompt: this.orchestratorPrompt

    };


    console.log(
      '🚀 ORCHESTRATOR - OPENCODE'
    );

    console.log(
      '📦 Body:',
      body
    );


    this.http.post<any>(

      `${this.apiUrl}/api/opencode/execute`,

      body

    ).subscribe({

      next: (response) => {

        console.log(
          '✅ OpenCode terminé:',
          response
        );


        this.orchestratorResult =
          response.opencode_result || '';


        this.orchestratorSuccess =
          response.success === true;


        this.orchestrating = false;

        this.orchestratorEditing = false;


        if (!this.orchestratorSuccess) {

          this.orchestratorFailed = true;

          this.orchestratorFailedStep = 5;

          this.errorMessage =
            response?.message ||
            'OpenCode a échoué.';

          return;
        }


        this.successMessage =
          'OpenCode a terminé avec succès.';
      },


      error: (error) => {

        console.error(
          '❌ Erreur OpenCode:',
          error
        );


        this.orchestrating = false;

        this.orchestratorSuccess = false;

        this.orchestratorFailed = true;

        this.orchestratorFailedStep = 5;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Erreur pendant l’exécution de OpenCode.'
          );
      }

    });
  }


  // ============================================================
  // ORCHESTRATOR SAVE PROMPT
  // ============================================================

  saveAndExecuteOrchestrator(): void {

    this.orchestratorEditing = false;

    this.executeOrchestratorPrompt();
  }


  // ============================================================
  // ORCHESTRATOR DEPLOY
  // ============================================================

  deployOrchestrator(): void {

    const key =
      this.normalizeIssueKey(
        this.orchestratorIssueKey
      );


    if (!key) {

      this.errorMessage =
        'Veuillez entrer une clé Jira.';

      return;
    }


    if (!this.orchestratorSuccess) {

      this.errorMessage =
        'Veuillez d’abord terminer OpenCode avec succès.';

      return;
    }


    this.orchestrating = true;

    this.orchestratorStep = 6;

    this.orchestratorDeployResult = null;

    this.orchestratorDeployed = false;

    this.errorMessage = '';

    this.successMessage = '';


    const body = {

      issue_key: key

    };


    console.log(
      '🚀 ORCHESTRATOR - DEPLOY'
    );

    console.log(
      '📦 Body:',
      body
    );


    this.http.post<any>(

      `${this.apiUrl}/api/git/deploy`,

      body

    ).subscribe({

      next: (response) => {

        console.log(
          '✅ Deploy orchestrateur:',
          response
        );


        this.orchestratorDeployResult =
          response;


        this.orchestrating = false;


        this.orchestratorDeployed =
          response?.success === true;


        if (this.orchestratorDeployed) {

          this.orchestratorSuccess = true;

          this.orchestratorStep = 6;

          this.successMessage =
            response?.message ||
            'Projet déployé sur GitHub avec succès.';

        } else {

          this.orchestratorFailed = true;

          this.orchestratorFailedStep = 6;

          this.errorMessage =
            response?.message ||
            'Le déploiement a échoué.';
        }
      },


      error: (error) => {

        console.error(
          '❌ Erreur Deploy orchestrateur:',
          error
        );


        this.orchestrating = false;

        this.orchestratorDeployed = false;

        this.orchestratorFailed = true;

        this.orchestratorFailedStep = 6;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Impossible de déployer le projet sur GitHub.'
          );
      }

    });
  }


  // ============================================================
  // STEP 1 - JIRA
  // ============================================================

  getTicket(): void {

    const key =
      this.normalizeIssueKey(
        this.stepIssueKey
      );


    if (!key) {

      this.errorMessage =
        'Veuillez entrer une clé Jira.';

      return;
    }


    this.stepIssueKey = key;

    this.stepLoading = true;

    this.errorMessage = '';

    this.stepTicket = null;

    this.stepAnalysis = '';

    this.stepPrompt = '';

    this.stepGitResult = null;

    this.stepResult = '';

    this.stepDeployResult = null;

    this.stepDeployed = false;

    this.stepSuccess = false;

    this.stepFailed = false;

    this.stepFailedStep = 0;


    const url =
      `${this.apiUrl}/api/jira/${encodeURIComponent(key)}`;


    console.log(
      '🔎 STEP 1 - GET JIRA:',
      url
    );


    this.http.get<any>(url).subscribe({

      next: (response) => {

        console.log(
          '✅ Ticket récupéré:',
          response
        );


        this.stepTicket =
          response;

        this.stepLoading = false;
      },


      error: (error) => {

        console.error(
          '❌ Erreur Jira:',
          error
        );


        this.stepLoading = false;

        this.stepFailed = true;

        this.stepFailedStep = 1;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Impossible de récupérer le ticket Jira.'
          );
      }

    });
  }


  // ============================================================
  // STEP 1 - EDIT TICKET
  // ============================================================

  editStepTicket(): void {

    if (!this.stepTicket) {
      return;
    }


    this.stepTicketBackup =
      JSON.parse(
        JSON.stringify(this.stepTicket)
      );


    this.stepTicketEditing = true;
  }


  saveStepTicket(): void {

    this.stepTicketEditing = false;

    this.stepTicketBackup = null;
  }


  ignoreStepTicket(): void {

    if (this.stepTicketBackup) {

      this.stepTicket =
        JSON.parse(
          JSON.stringify(this.stepTicketBackup)
        );
    }


    this.stepTicketEditing = false;

    this.stepTicketBackup = null;
  }


  // ============================================================
  // STEP 2 - ANALYSIS
  // ============================================================

  analyzeTicket(): void {

    if (!this.stepTicket) {

      this.errorMessage =
        'Veuillez d’abord récupérer le ticket Jira.';

      return;
    }


    this.stepLoading = true;

    this.errorMessage = '';

    this.stepAnalysis = '';

    this.stepPrompt = '';

    this.stepGitResult = null;

    this.stepResult = '';

    this.stepDeployResult = null;

    this.stepDeployed = false;

    this.stepSuccess = false;

    this.stepFailed = false;

    this.stepFailedStep = 0;


    const body = {

      ticket: this.stepTicket

    };


    console.log(
      '🧠 STEP 2 - ANALYSIS'
    );

    console.log(
      '📦 Body:',
      body
    );


    this.http.post<any>(

      `${this.apiUrl}/api/analysis`,

      body

    ).subscribe({

      next: (response) => {

        console.log(
          '✅ Analysis reçue:',
          response
        );


        this.stepAnalysis =
          response.analysis || '';


        this.stepAnalysisEditing = false;

        this.stepLoading = false;
      },


      error: (error) => {

        console.error(
          '❌ Erreur Analysis:',
          error
        );


        this.stepLoading = false;

        this.stepFailed = true;

        this.stepFailedStep = 2;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Impossible de générer l’analyse.'
          );
      }

    });
  }


  // ============================================================
  // STEP 2 - EDIT ANALYSIS
  // ============================================================

  editStepAnalysis(): void {

    if (!this.stepAnalysis) {
      return;
    }


    this.stepAnalysisBackup =
      this.stepAnalysis;


    this.stepAnalysisEditing = true;
  }


  saveStepAnalysis(): void {

    this.stepAnalysisEditing = false;

    this.stepAnalysisBackup = '';
  }


  ignoreStepAnalysis(): void {

    this.stepAnalysis =
      this.stepAnalysisBackup;


    this.stepAnalysisEditing = false;

    this.stepAnalysisBackup = '';
  }


  // ============================================================
  // STEP 3 - PROMPT
  // ============================================================

  generateStepPrompt(): void {

    if (!this.stepTicket) {

      this.errorMessage =
        'Veuillez d’abord récupérer le ticket Jira.';

      return;
    }


    if (!this.stepAnalysis) {

      this.errorMessage =
        'Veuillez d’abord analyser le ticket.';

      return;
    }


    this.stepLoading = true;

    this.errorMessage = '';

    this.stepPrompt = '';

    this.stepGitResult = null;

    this.stepResult = '';

    this.stepDeployResult = null;

    this.stepDeployed = false;

    this.stepFailed = false;

    this.stepFailedStep = 0;


    const body = {

      ticket: this.stepTicket,

      analysis: this.stepAnalysis

    };


    console.log(
      '📝 STEP 3 - PROMPT'
    );

    console.log(
      '📦 Body:',
      body
    );


    this.http.post<any>(

      `${this.apiUrl}/api/prompt`,

      body

    ).subscribe({

      next: (response) => {

        console.log(
          '✅ Prompt généré:',
          response
        );


        this.stepPrompt =
          response.prompt || '';


        this.stepPromptEditing = false;

        this.stepLoading = false;

        if (this.stepPrompt) {
          this.prepareGit();
        }
      },


      error: (error) => {

        console.error(
          '❌ Erreur Prompt:',
          error
        );


        this.stepLoading = false;

        this.stepFailed = true;

        this.stepFailedStep = 3;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Impossible de générer le prompt.'
          );
      }

    });
  }


  // ============================================================
  // STEP 3 - EDIT PROMPT
  // ============================================================

  editStepPrompt(): void {

    if (!this.stepPrompt) {
      return;
    }


    this.stepPromptBackup =
      this.stepPrompt;


    this.stepPromptEditing = true;
  }


  saveStepPrompt(): void {

    this.stepPromptEditing = false;

    this.stepPromptBackup = '';
  }


  ignoreStepPrompt(): void {

    this.stepPrompt =
      this.stepPromptBackup;


    this.stepPromptEditing = false;

    this.stepPromptBackup = '';
  }


  // ============================================================
  // STEP 4 - GIT PREPARATION
  // ============================================================

  prepareGit(): void {

    const key =
      this.normalizeIssueKey(
        this.stepIssueKey
      );


    console.log(
      '============================================'
    );

    console.log(
      '🔀 STEP 4 - GIT PREPARE'
    );

    console.log(
      '🎯 Jira Issue Key:',
      key
    );

    console.log(
      '============================================'
    );


    if (!key) {

      this.errorMessage =
        'Veuillez entrer une clé Jira.';

      return;
    }


    this.stepIssueKey = key;

    this.stepLoading = true;

    this.errorMessage = '';

    this.successMessage = '';

    this.stepGitResult = null;

    this.stepSuccess = false;

    this.stepFailed = false;

    this.stepFailedStep = 0;


    const body = {

      issue_key: key,

    };


    console.log(
      '📦 BODY /api/git/prepare:',
      JSON.stringify(body, null, 2)
    );


    console.log(
      '🔗 URL:',
      `${this.apiUrl}/api/git/prepare`
    );


    this.http.post<any>(

      `${this.apiUrl}/api/git/prepare`,

      body

    ).subscribe({

      next: (response) => {

        console.log(
          '✅ Git preparation terminée:',
          response
        );


        this.stepGitResult =
          response;


        this.stepLoading = false;


        this.stepSuccess =
          response?.success === true;


        if (this.stepSuccess) {

          this.successMessage =
            response?.message ||
            'Repository Git préparé avec succès.';

        } else {

          this.stepFailed = true;

          this.stepFailedStep = 4;

          this.errorMessage =
            response?.message ||
            'La préparation Git a échoué.';
        }
      },


      error: (error) => {

        console.error(
          '❌ Erreur Git:',
          error
        );


        this.stepLoading = false;

        this.stepSuccess = false;

        this.stepFailed = true;

        this.stepFailedStep = 4;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Impossible de préparer le repository Git.'
          );
      }

    });
  }


  // ============================================================
  // STEP 5 - OPENCODE
  // ============================================================

  executeStepPrompt(): void {

    const key =
      this.normalizeIssueKey(
        this.stepIssueKey
      );


    if (!key) {

      this.errorMessage =
        'Veuillez entrer une clé Jira.';

      return;
    }


    if (!this.stepPrompt.trim()) {

      this.errorMessage =
        'Le prompt est vide.';

      return;
    }


    if (!this.stepGitResult) {

      this.errorMessage =
        'Veuillez d’abord préparer le repository Git.';

      return;
    }


    if (
      this.stepGitResult?.success !== true
    ) {

      this.errorMessage =
        'La préparation Git n’a pas réussi.';

      return;
    }


    if (this.stepPromptEditing) {

      this.errorMessage =
        'Veuillez enregistrer ou ignorer la modification du prompt avant l’exécution.';

      return;
    }


    this.stepLoading = true;

    this.errorMessage = '';

    this.successMessage = '';

    this.stepResult = '';

    this.stepSuccess = false;

    this.stepFailed = false;

    this.stepFailedStep = 0;

    this.stepDeployResult = null;

    this.stepDeployed = false;


    const body = {

      issue_key: key,

      prompt: this.stepPrompt

    };


    console.log(
      '🚀 STEP 5 - OPENCODE'
    );

    console.log(
      '📦 Body:',
      body
    );


    this.http.post<any>(

      `${this.apiUrl}/api/opencode/execute`,

      body

    ).subscribe({

      next: (response) => {

        console.log(
          '✅ OpenCode terminé:',
          response
        );


        this.stepResult =
          response.opencode_result || '';


        this.stepSuccess =
          response.success === true;


        this.stepLoading = false;


        if (!this.stepSuccess) {

          this.stepFailed = true;

          this.stepFailedStep = 5;

          this.errorMessage =
            response?.message ||
            'OpenCode a échoué.';

        } else {

          this.successMessage =
            'OpenCode a terminé avec succès.';
        }
      },


      error: (error) => {

        console.error(
          '❌ Erreur OpenCode:',
          error
        );


        this.stepLoading = false;

        this.stepSuccess = false;

        this.stepResult = '';

        this.stepFailed = true;

        this.stepFailedStep = 5;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Erreur pendant l’exécution de OpenCode.'
          );
      }

    });
  }


  // ============================================================
  // STEP 6 - DEPLOY
  // ============================================================

  deployStepByStep(): void {

    const key =
      this.normalizeIssueKey(
        this.stepIssueKey
      );


    if (!key) {

      this.errorMessage =
        'Veuillez entrer une clé Jira.';

      return;
    }


    if (!this.stepSuccess) {

      this.errorMessage =
        'Veuillez d’abord terminer OpenCode avec succès.';

      return;
    }


    this.stepLoading = true;

    this.stepDeployResult = null;

    this.stepDeployed = false;

    this.errorMessage = '';

    this.successMessage = '';

    this.stepFailed = false;

    this.stepFailedStep = 0;


    const body = {

      issue_key: key

    };


    console.log(
      '🚀 STEP 6 - DEPLOY'
    );

    console.log(
      '📦 Body:',
      body
    );


    this.http.post<any>(

      `${this.apiUrl}/api/git/deploy`,

      body

    ).subscribe({

      next: (response) => {

        console.log(
          '✅ Deploy Step-by-Step:',
          response
        );


        this.stepDeployResult =
          response;


        this.stepLoading = false;


        this.stepDeployed =
          response?.success === true;


        if (this.stepDeployed) {

          this.stepSuccess = true;

          this.successMessage =
            response?.message ||
            'Projet déployé sur GitHub avec succès.';

        } else {

          this.stepFailed = true;

          this.stepFailedStep = 6;

          this.errorMessage =
            response?.message ||
            'Le déploiement a échoué.';
        }
      },


      error: (error) => {

        console.error(
          '❌ Erreur Deploy:',
          error
        );


        this.stepLoading = false;

        this.stepDeployed = false;

        this.stepFailed = true;

        this.stepFailedStep = 6;


        this.errorMessage =
          this.getApiErrorMessage(
            error,
            'Impossible de déployer le projet sur GitHub.'
          );
      }

    });
  }


  // ============================================================
  // COPY STEP PROMPT
  // ============================================================

  copyStepPrompt(): void {

    if (!this.stepPrompt) {
      return;
    }


    navigator.clipboard
      .writeText(this.stepPrompt)

      .then(() => {

        console.log(
          '✅ Prompt copié'
        );


        this.successMessage =
          'Prompt copié dans le presse-papiers.';
      })


      .catch((error) => {

        console.error(
          '❌ Erreur copie:',
          error
        );


        this.errorMessage =
          'Impossible de copier le prompt.';
      });
  }


  // ============================================================
  // COPY ORCHESTRATOR PROMPT
  // ============================================================

  copyOrchestratorPrompt(): void {

    if (!this.orchestratorPrompt) {
      return;
    }


    navigator.clipboard
      .writeText(this.orchestratorPrompt)

      .then(() => {

        console.log(
          '✅ Prompt orchestrateur copié'
        );


        this.successMessage =
          'Prompt copié dans le presse-papiers.';
      })


      .catch((error) => {

        console.error(
          '❌ Erreur copie:',
          error
        );


        this.errorMessage =
          'Impossible de copier le prompt.';
      });
  }

}