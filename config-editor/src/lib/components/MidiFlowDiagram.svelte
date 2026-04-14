<script lang="ts">
	import { config } from '$lib/formStore';
	import { formatChannelShort } from '$lib/utils';
	import type { ButtonConfig, MidiCommand, CommandOrConditional, ConditionalCommand } from '$lib/types';

	interface Props {
		button: ButtonConfig | null;
		buttonIndex: number;
	}

	let { button, buttonIndex }: Props = $props();

	interface FlowNode {
		id: string;
		type: 'source' | 'event' | 'command' | 'destination' | 'conditional';
		label: string;
		details?: string[];
		commands?: MidiCommand[];
		condition?: any;
		branches?: { then: FlowNode[]; else: FlowNode[] };
		hasCondition?: boolean;
	}

	// Type guard for ConditionalCommand
	function isConditional(cmd: CommandOrConditional): cmd is ConditionalCommand {
		return 'type' in cmd && cmd.type === 'conditional';
	}

	// Parse button config into flow nodes
	function parseButtonFlow(btnConfig: ButtonConfig, currentConfig: typeof $config): Map<string, FlowNode[]> {
		const eventMap = new Map<string, FlowNode[]>();

		// Helper to create legacy command from button config
		function createLegacyCommand(btnCfg: ButtonConfig, isOn: boolean): MidiCommand | null {
			const type = btnCfg.type ?? 'cc';
			const channel = btnCfg.channel;

			switch (type) {
				case 'cc':
					if (btnCfg.cc === undefined) return null;
					return {
						type: 'cc',
						cc: btnCfg.cc,
						value: isOn ? (btnCfg.cc_on ?? btnCfg.value_on ?? 127) : (btnCfg.cc_off ?? btnCfg.value_off ?? 0),
						channel
					};
				case 'note':
					if (btnCfg.note === undefined) return null;
					return {
						type: 'note',
						note: btnCfg.note,
						velocity: isOn ? (btnCfg.velocity_on ?? 127) : (btnCfg.velocity_off ?? 0),
						channel
					};
				case 'pc':
					if (btnCfg.program === undefined) return null;
					return {
						type: 'pc',
						program: btnCfg.program,
						channel
					};
				case 'pc_inc':
					return {
						type: 'pc_inc',
						pc_step: btnCfg.pc_step ?? 1,
						channel
					};
				case 'pc_dec':
					return {
						type: 'pc_dec',
						pc_step: btnCfg.pc_step ?? 1,
						channel
					};
				default:
					return null;
			}
		}

		// Helper to format command for display
		function formatCommand(cmd: MidiCommand): string[] {
			const details: string[] = [];
			const ch = cmd.channel !== undefined 
				? ` (${formatChannelShort(cmd.channel, currentConfig)})` 
				: '';

			switch (cmd.type) {
				case 'cc':
					details.push(`CC${cmd.cc} = ${cmd.value}${ch}`);
					break;
				case 'note':
					details.push(`Note${cmd.note} vel${cmd.velocity}${ch}`);
					break;
				case 'pc':
					details.push(`PC${cmd.program}${ch}`);
					break;
				case 'pc_inc':
					details.push(`PC +${cmd.pc_step || 1}${ch}`);
					break;
				case 'pc_dec':
					details.push(`PC -${cmd.pc_step || 1}${ch}`);
					break;
			}
			return details;
		}

		// Process each event type
		const events = [
			{ key: 'press', label: 'PRESS' },
			{ key: 'release', label: 'RELEASE' },
			{ key: 'long_press', label: 'LONG PRESS' },
			{ key: 'long_release', label: 'LONG RELEASE' },
			{ key: 'double_press', label: 'DOUBLE PRESS' }
		];

		events.forEach(({ key, label }) => {
			let commands = btnConfig[key as keyof ButtonConfig] as CommandOrConditional[] | undefined;
			
			// Check for state overrides first (keytimes)
			if ((!commands || commands.length === 0) && btnConfig.states && btnConfig.states.length > 0) {
				// Collect all non-empty commands from all states for this event
				const stateCommands: CommandOrConditional[] = [];
				btnConfig.states.forEach((state, idx) => {
					const stateEventCmds = state[key as keyof typeof state] as CommandOrConditional[] | undefined;
					if (stateEventCmds && stateEventCmds.length > 0) {
						stateCommands.push(...stateEventCmds);
					}
				});
				if (stateCommands.length > 0) {
					commands = stateCommands;
				}
			}
			
			// Fallback to legacy format if no event arrays exist
			if (!commands || commands.length === 0) {
				// Check if button has any legacy MIDI fields (cc, note, program)
				const hasLegacyFields = btnConfig.cc !== undefined || 
				                       btnConfig.note !== undefined || 
				                       btnConfig.program !== undefined ||
				                       btnConfig.pc_step !== undefined;
				
				if (key === 'press' && hasLegacyFields) {
					const legacyCmd = createLegacyCommand(btnConfig, true);
					if (legacyCmd) commands = [legacyCmd];
				} else if (key === 'release' && hasLegacyFields) {
					// Only show release for toggle/select/normal modes, not for PC types or momentary
					const mode = btnConfig.mode ?? 'toggle';
							const type = btnConfig.type ?? 'cc';
					const showRelease = (mode === 'toggle' || mode === 'select' || mode === 'normal') && 
					                   (type === 'cc' || type === 'note');
					if (showRelease) {
						const legacyCmd = createLegacyCommand(btnConfig, false);
						if (legacyCmd) commands = [legacyCmd];
					}
				}
			}
			
			if (commands && commands.length > 0) {
				const nodes: FlowNode[] = [];

				commands.forEach((cmd, idx) => {
					if (isConditional(cmd)) {
						// Create conditional node with branches
						const condNode: FlowNode = {
							id: `${key}-cond-${idx}`,
							type: 'conditional',
							label: 'Conditional',
							condition: cmd.if,
							hasCondition: true,
							branches: {
								then: (cmd.then || []).map((thenCmd, tIdx) => ({
									id: `${key}-cond-${idx}-then-${tIdx}`,
									type: 'command',
									label: 'Then',
									details: isConditional(thenCmd) ? ['⚡ Nested Conditional'] : formatCommand(thenCmd)
								})),
								else: (cmd.else || []).map((elseCmd, eIdx) => ({
									id: `${key}-cond-${idx}-else-${eIdx}`,
									type: 'command',
									label: 'Else',
									details: isConditional(elseCmd) ? ['⚡ Nested Conditional'] : formatCommand(elseCmd)
								}))
							}
						};
						nodes.push(condNode);
					} else {
						// Regular command node
						nodes.push({
							id: `${key}-${idx}`,
							type: 'command',
							label: `Command ${idx + 1}`,
							details: formatCommand(cmd),
							hasCondition: false
						});
					}
				});

				eventMap.set(label, nodes);
			}
		});

		return eventMap;
	}

	let flowData = $derived(button ? parseButtonFlow(button, $config) : new Map());
	let hasAnyEvents = $derived(flowData.size > 0);
	let buttonLabel = $derived(button?.label || `Button ${buttonIndex + 1}`);
	let selectGroup = $derived(button?.select_group);
	let keytimes = $derived(button?.keytimes);
</script>

{#if !button}
	<div class="midi-flow empty">
		<p class="empty-message">Select a button to view MIDI flow</p>
	</div>
{:else}
<div class="midi-flow">
	<div class="flow-header">
		<h3 class="flow-title">MIDI FLOW</h3>
		<div class="flow-subtitle">{buttonLabel}</div>
		{#if selectGroup}
			<div class="badge select-group">Select Group: {selectGroup}</div>
		{/if}
		{#if keytimes && keytimes > 1}
			<div class="badge keytimes">Keytimes: {keytimes} states</div>
		{/if}
	</div>

	{#if !hasAnyEvents}
		<div class="empty-state">
			<p>No MIDI commands configured</p>
			<p class="hint">Add commands using the buttons below</p>
		</div>
	{:else}
		<div class="flow-diagram">
			<!-- Source Node -->
			<div class="node source-node">
				<div class="node-content">{buttonLabel}</div>
			</div>

			<!-- Event Flows -->
			<div class="events-container">
				{#each Array.from(flowData.entries()) as [eventLabel, nodes]}
					<div class="event-flow">
						<!-- Event Node -->
						<div class="connector" />
						<div class="node event-node {eventLabel.toLowerCase().replace(/\s+/g, '-')}">
							<div class="node-label">{eventLabel}</div>
							<div class="node-count">×{nodes.length}</div>
						</div>

						<!-- Command Nodes -->
						<div class="commands-group">
							{#each nodes as node}
								<div class="connector" />
								{#if node.type === 'conditional'}
									<!-- Conditional Branch -->
									<div class="conditional-container">
										<div class="node conditional-node">
											<div class="node-content">
												<div class="conditional-icon">⚡</div>
												<div class="conditional-label">Conditional</div>
											</div>
										</div>

										<!-- Then Branch -->
										{#if node.branches && node.branches.then.length > 0}
											<div class="branch then-branch">
												<div class="branch-label">THEN</div>
												{#each node.branches.then as thenNode}
													<div class="node command-node then">
														<div class="node-content">
															{#each thenNode.details || [] as detail}
																<div class="command-detail">{detail}</div>
															{/each}
														</div>
													</div>
												{/each}
												<div class="connector" />
												<div class="node dest-node">Host</div>
											</div>
										{/if}

										<!-- Else Branch -->
										{#if node.branches && node.branches.else.length > 0}
											<div class="branch else-branch">
												<div class="branch-label">ELSE</div>
												{#each node.branches.else as elseNode}
													<div class="node command-node else">
														<div class="node-content">
															{#each elseNode.details || [] as detail}
																<div class="command-detail">{detail}</div>
															{/each}
														</div>
													</div>
												{/each}
												<div class="connector" />
												<div class="node dest-node">Host</div>
											</div>
										{/if}
									</div>
								{:else}
									<!-- Regular Command -->
									<div class="node command-node">
										<div class="node-content">
											{#each node.details || [] as detail}
												<div class="command-detail">{detail}</div>
											{/each}
										</div>
									</div>
									<div class="connector" />
									<div class="node dest-node">Host</div>
								{/if}
							{/each}
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>
{/if}

<style>
	.midi-flow {
		background: var(--bg-card);
		border: 1px solid var(--border-default);
		border-radius: 10px;
		padding: 20px 24px;
		margin: 12px 16px;
		box-shadow: var(--shadow-sm);
	}

	.flow-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		margin-bottom: 1rem;
		padding-bottom: 0.75rem;
		border-bottom: 2px solid #2a2a2a;
		flex-wrap: wrap;
	}

	.flow-title {
		font-size: var(--text-lg);
		font-weight: 700;
		color: var(--text-primary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin: 0;
	}

	.flow-subtitle {
		font-size: var(--text-sm);
		font-weight: 600;
		color: var(--text-secondary);
	}

	.badge {
		padding: 4px 12px;
		border-radius: 12px;
		font-size: 12px;
		font-weight: 500;
	}

	.select-group {
		background: rgba(139, 92, 246, 0.2);
		color: #a78bfa;
		border: 1px solid rgba(139, 92, 246, 0.3);
	}

	.keytimes {
		background: rgba(59, 130, 246, 0.2);
		color: #60a5fa;
		border: 1px solid rgba(59, 130, 246, 0.3);
	}

	.empty-state {
		text-align: center;
		padding: 2rem;
		color: var(--text-secondary);
	}

	.empty-state p {
		margin: 8px 0;
	}

	.hint {
		font-size: 14px;
		color: var(--text-tertiary);
	}

	.flow-diagram {
		display: flex;
		flex-direction: row;
		align-items: stretch;
		gap: 16px;
		overflow-x: auto;
		padding: 0;
	}

	.node {
		border: 2px solid;
		border-radius: 8px;
		padding: 12px 20px;
		background: var(--bg-input);
		min-width: 120px;
		text-align: center;
	}

	.source-node {
		border-color: #4ade80;
		background: rgba(74, 222, 128, 0.1);
		flex-shrink: 0;
	}

	.source-node .node-content {
		font-size: 16px;
		font-weight: 600;
		color: #4ade80;
	}

	.events-container {
		display: flex;
		flex-direction: column;
		justify-content: center;
		gap: 20px;
		flex: 1;
	}

	.event-flow {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 8px;
	}

	.event-node {
		border-color: #22d3ee;
		background: rgba(34, 211, 238, 0.1);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
	}

	.node-label {
		font-weight: 600;
		color: #22d3ee;
		font-size: 14px;
	}

	.node-count {
		font-size: 12px;
		color: var(--text-tertiary);
	}

	.connector {
		width: 24px;
		height: 2px;
		background: linear-gradient(to right, var(--border-default), transparent);
	}

	.commands-group {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 8px;
	}

	.command-node {
		border-color: #fbbf24;
		background: rgba(251, 191, 36, 0.1);
		min-width: 200px;
	}

	.command-node.then {
		border-color: #4ade80;
		background: rgba(74, 222, 128, 0.1);
	}

	.command-node.else {
		border-color: #f87171;
		background: rgba(248, 113, 113, 0.1);
	}

	.node-content {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.command-detail {
		font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
		font-size: 13px;
		color: #fbbf24;
	}

	.command-node.then .command-detail {
		color: #4ade80;
	}

	.command-node.else .command-detail {
		color: #f87171;
	}

	.conditional-container {
		display: flex;
		flex-direction: column;
		gap: 8px;
		align-items: stretch;
	}

	.conditional-node {
		border-color: #a78bfa;
		background: rgba(167, 139, 250, 0.1);
		display: flex;
		justify-content: center;
	}

	.conditional-node .node-content {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 8px;
	}

	.conditional-icon {
		font-size: 20px;
	}

	.conditional-label {
		font-weight: 600;
		color: #a78bfa;
	}

	.branch {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 8px;
		padding: 8px 12px;
		border: 1px dashed var(--border-default);
		border-radius: 8px;
		background: var(--bg-dark);
		min-width: 300px;
	}

	.branch-label {
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 0.5px;
		padding: 4px 12px;
		border-radius: 12px;
	}

	.then-branch .branch-label {
		background: rgba(74, 222, 128, 0.2);
		color: #4ade80;
	}

	.else-branch .branch-label {
		background: rgba(248, 113, 113, 0.2);
		color: #f87171;
	}

	.dest-node {
		border-color: #6366f1;
		background: rgba(99, 102, 241, 0.1);
		color: #6366f1;
		font-weight: 600;
		font-size: 14px;
	}

	.midi-flow.empty {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 200px;
	}

	.empty-message {
		color: var(--text-secondary);
		font-style: italic;
		font-size: 14px;
	}
</style>
