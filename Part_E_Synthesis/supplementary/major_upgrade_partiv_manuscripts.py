#!/usr/bin/env python3
"""Apply the reproducible major-depth upgrade to every Part IV manuscript.

The manuscripts remain standalone papers. This script adds one paper-specific
mechanistic section, one native TikZ diagram, an evidence ladder, and explicit
connections to the verified CDFD and external reference layer. It is
idempotent: rerunning it replaces only the marked upgrade block.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


def _find_release_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "Part_A_Earth_Systems").is_dir() and (candidate / "Part_E_Synthesis").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CDFD Part IV release root")


RELEASE_ROOT = _find_release_root()
BEGIN_MARKER = "% BEGIN PART IV MAJOR UNIVERSAL UPGRADE"
END_MARKER = "% END PART IV MAJOR UNIVERSAL UPGRADE"


@dataclass(frozen=True)
class Profile:
    drive: str
    constraint: str
    response: str
    memory: str
    outcome: str
    evidence: str
    stress: str
    falsifier: str
    scale: str


P = Profile
PROFILES: dict[str, Profile] = {
    "A-01": P("radiative, hydrological, biogeochemical, and human forcing", "transport resistance and finite environmental capacity", "circulation, storage, ecological buffering, and rerouting", "soil, ice, ocean, ecological, and contamination legacies", "redistribution, overload, recovery, and regime change", "coupled reanalysis, remote sensing, gauge records, and ecological time series", "a compound heat, rainfall, and pollutant pulse", "the added variables do not improve prediction beyond ordinary coupled transport budgets", "hours to millennia; catchments to the coupled Earth system"),
    "A-02": P("differential solar heating, latent heat, and moisture transport", "static stability, friction, topography, and radiative limits", "convection, waves, circulation, and cloud adjustment", "soil moisture, sea-surface temperature, aerosol, and ice states", "circulation strength, precipitation, and extreme-event persistence", "reanalysis, radiosondes, satellite radiation, and precipitation products", "a sustained heat and moisture anomaly", "the mapping cannot predict circulation or recovery residuals beyond standard atmospheric equations", "minutes to decades; boundary layers to planetary circulation"),
    "A-03": P("wind stress, buoyancy forcing, tides, and freshwater input", "bathymetry, stratification, friction, and mixing limits", "eddies, overturning, mixing, and boundary-current adjustment", "heat, salinity, oxygen, and circulation history", "heat transport, ventilation, current strength, and recovery", "Argo profiles, altimetry, moorings, tracers, and hydrography", "a freshwater or heat pulse applied to a stratified basin", "the CDFD variables add no out-of-sample skill beyond ocean circulation models", "hours to centuries; turbulence to global overturning"),
    "A-04": P("precipitation, snowmelt, groundwater pressure, and gravity", "channel conveyance, infiltration, storage, and sediment resistance", "floodplain storage, wetland buffering, infiltration, and channel adjustment", "soil moisture, groundwater, channel incision, and sediment legacy", "discharge, flood extent, avulsion, and recovery time", "stream gauges, soil-moisture products, topography, sediment records, and flood maps", "an extreme rainfall pulse followed by a dry recovery interval", "hysteresis and recovery are explained equally well without explicit structural memory", "minutes to millennia; hillslopes to continental basins"),
    "A-05": P("weathering, water, organic inputs, roots, and land-use pressure", "porosity, nutrient limitation, mineralogy, and erosion", "aggregation, bioturbation, root growth, and microbial turnover", "compaction, contamination, horizon development, and carbon legacy", "infiltration, fertility, carbon retention, and erosion resistance", "soil profiles, long-term field trials, spectroscopy, infiltration tests, and carbon records", "repeated cultivation or drought followed by restoration", "soil recovery is independent of prior-load history after controlling for present conditions", "days to millennia; aggregates to landscapes"),
    "A-06": P("solar energy, nutrients, biomass production, and consumer demand", "stoichiometry, trophic bottlenecks, habitat limits, and loss", "functional diversity, migration, storage, and trophic rerouting", "community composition, soil state, disturbance, and evolutionary legacy", "productivity, respiration, transfer efficiency, and recovery", "flux towers, food-web observations, isotope tracers, productivity, and respiration records", "a resource pulse followed by drought, harvest, or consumer loss", "the proposed constraint-memory terms do not explain transfer efficiency or recovery", "seconds to centuries; organisms to biomes"),
    "A-07": P("colonization, energy supply, disturbance, and environmental change", "habitat area, fragmentation, resource limits, and interaction structure", "functional redundancy, dispersal, refugia, and adaptation", "extinction debt, genetic erosion, invasion, and disturbance history", "persistence, turnover, function, and extinction risk", "species inventories, occupancy time series, trait data, genetics, and remote sensing", "fragmentation followed by reconnection or habitat restoration", "prior fragmentation history does not alter recovery after present habitat is matched", "generations to millennia; populations to biomes"),
    "A-08": P("chemical, particulate, thermal, biological, and noise loads", "dilution, adsorption, transformation, and clearance capacity", "bioremediation, sequestration, treatment, and pathway rerouting", "bioaccumulation, sediment reservoirs, tissue burden, and legacy waste", "exposure, toxicity, transport distance, and recovery", "emissions inventories, water and air monitoring, biomarkers, sediments, and ecotoxicology", "a controlled contaminant pulse and subsequent source removal", "legacy and responsiveness terms fail to improve exposure or recovery forecasts", "minutes to centuries; organisms to airsheds and watersheds"),
    "A-09": P("fertilizer, water, energy, labor, capital, and production demand", "soil, water, pest, biodiversity, and infrastructure limits", "crop diversity, management, storage, irrigation, and substitution", "soil degradation, resistance, farm capital, and management history", "yield, yield variance, externalities, and recovery", "long-term agricultural trials, yield records, soil assays, remote sensing, and input accounts", "input intensification followed by drought or input withdrawal", "the framework cannot distinguish durable yield from short-lived throughput gains", "seasons to centuries; fields to food systems"),
    "A-10": P("human demand for energy, materials, food, land, and welfare", "regenerative capacity, pollution sinks, institutions, and distribution", "innovation, substitution, repair, governance, and demand adjustment", "infrastructure lock-in, ecological degradation, wealth, and institutional history", "durable welfare within environmental and social limits", "material-flow accounts, life-cycle inventories, ecological indicators, and welfare series", "a demand increase combined with a capacity loss", "the framework cannot outperform established sustainability accounting or identify trade-offs", "years to centuries; communities to the planet"),
    "A-11": P("compound climatic, ecological, geophysical, and human forcing", "shrinking buffers, connectivity bottlenecks, and finite recovery capacity", "refugia, redundancy, migration, repair, and coordinated response", "cumulative damage, lost diversity, degraded infrastructure, and prior shocks", "cascade size, tipping risk, loss, and recovery", "paleorecords, hazard databases, ecological monitoring, infrastructure records, and recovery series", "two individually tolerable shocks applied in close succession", "compound history does not change the response once present load is controlled", "minutes to millennia; local failures to planetary cascades"),
    "A-12": P("coupled flows of energy, water, matter, organisms, and human activity", "interacting capacities and bottlenecks across Earth subsystems", "cross-system buffering, redistribution, adaptation, and repair", "shared climatic, ecological, geological, and institutional legacies", "whole-system resilience, cascade containment, and recovery", "coupled Earth-system observations, network reconstructions, and multi-hazard records", "a synchronized perturbation across two or more Earth-system pathways", "cross-domain coupling adds no explanatory or predictive value", "minutes to geological time; local interfaces to the coupled Earth system"),
    "A-13": P("mantle heat, buoyancy, slab pull, ridge push, and stress transfer", "lithospheric strength, friction, geometry, and phase boundaries", "fault redistribution, ductile flow, melting, and plate reorganization", "inherited faults, thermal history, compositional structure, and prior strain", "deformation, seismicity, volcanism, and tectonic reorganization", "geodesy, seismicity, tomography, heat flow, structural geology, and paleomagnetism", "a stress-transfer sequence across a mapped fault network", "explicit memory and network terms do not improve forecasts or retrospective explanation", "seconds to hundreds of millions of years; grains to plates"),
    "A-14": P("magma buoyancy, volatile pressure, heat, and tectonic forcing", "conduit geometry, rock strength, crystallization, and degassing limits", "deformation, fracture, vent opening, convection, and pressure release", "chamber recharge, crystal mush, conduit scars, and edifice history", "unrest, eruption style, magnitude, and recovery", "seismicity, deformation, gas, petrology, thermal imagery, and eruption chronologies", "a recharge pulse into systems with contrasting histories", "history-sensitive variables do not improve eruption-style or unrest interpretation", "seconds to millennia; bubbles and conduits to volcanic arcs"),
    "B-01": P("demand across energy, water, transport, communication, and public services", "component capacity, coupling, dependency, and maintenance limits", "redundancy, rerouting, control, repair, and demand management", "aging, backlog, design choices, and prior incidents", "service continuity, cascade size, restoration, and equity", "sensor streams, service logs, asset registers, dependency maps, and incident records", "a localized component loss during peak cross-service demand", "coupled CDFD variables do not improve failure or restoration prediction", "milliseconds to decades; components to national infrastructure"),
    "B-02": P("electrical demand, generation, and renewable variability", "thermal limits, stability margins, transmission, and reserve capacity", "dispatch, storage, demand response, protection, and islanding", "equipment aging, network state, prior contingencies, and operator learning", "frequency stability, congestion, unserved energy, and restoration", "phasor measurements, dispatch records, topology, outage logs, and asset health", "a line or generator loss during high demand", "the mapping adds no value beyond established power-flow and stability models", "milliseconds to decades; devices to interconnections"),
    "B-03": P("packet demand, route announcements, and application traffic", "bandwidth, queue capacity, latency, policy, and physical links", "routing, congestion control, caching, and traffic engineering", "cached state, route history, failure scars, and protocol configuration", "throughput, delay, loss, reachability, and recovery", "packet traces, queue telemetry, routing tables, topology, and outage records", "a traffic surge combined with a route or link failure", "memory-aware terms do not improve congestion or recovery forecasts", "microseconds to years; flows to the global Internet"),
    "B-04": P("tasks, data, synchronization, and user demand", "compute, memory, network, storage, and consistency limits", "scheduling, replication, autoscaling, partitioning, and failover", "queues, caches, checkpoints, state, and technical debt", "latency, throughput, correctness, cost, and recovery", "traces, scheduler logs, dependency graphs, resource metrics, and failure injections", "a burst load combined with a node or network partition", "the added state variables do not improve performance or failure prediction", "nanoseconds to years; processes to global services"),
    "B-05": P("signals, training examples, gradients, and inference demand", "compute, data quality, architecture, bandwidth, and noise", "learning, attention, sparsity, regularization, and plasticity", "weights, optimizer state, replay history, and accumulated bias", "accuracy, calibration, generalization, and adaptation", "learning curves, activation traces, gradient statistics, ablations, and benchmark shifts", "a distribution shift or capacity bottleneck after training", "explicit constraint-memory variables do not improve generalization or adaptation forecasts", "nanoseconds to model lifetimes; units to learning ecosystems"),
    "B-06": P("mobility, water, energy, waste, housing, and communication demand", "road, pipe, grid, land, fiscal, and governance capacity", "multimodal routing, maintenance, planning, pricing, and mutual aid", "built form, segregation, deferred maintenance, and investment history", "access, reliability, congestion, health, and recovery", "mobility traces, utility telemetry, land use, budgets, service access, and incident records", "a heat, flood, or demand shock across coupled urban services", "the framework cannot identify failures or inequities beyond ordinary urban models", "minutes to centuries; blocks to metropolitan regions"),
    "B-07": P("orders, shipments, materials, and customer demand", "vehicle, warehouse, port, labor, and information capacity", "rerouting, inventory, substitution, prioritization, and coordination", "contracts, inventories, path dependence, and disruption history", "lead time, fill rate, cost, shortage, and recovery", "shipment traces, inventory records, network maps, lead times, and disruption logs", "a supplier or corridor loss during a demand surge", "memory and topology terms do not improve shortage or recovery prediction", "hours to decades; parcels to global trade networks"),
    "B-08": P("requests, data, jobs, and service dependencies", "compute, network, storage, power, and budget limits", "autoscaling, load balancing, caching, failover, and degradation", "cached state, incident history, configuration, and technical debt", "latency, availability, cost, error rate, and restoration", "service telemetry, traces, dependency graphs, change logs, and incident reports", "a demand spike combined with a dependency or regional failure", "the model adds no predictive value beyond queueing and reliability engineering", "microseconds to years; containers to multi-region services"),
    "B-09": P("queries, facts, relations, and update streams", "schema, compute, provenance, consistency, and quality limits", "inference, curation, indexing, schema evolution, and conflict resolution", "accumulated ontology, provenance, stale facts, and design decisions", "retrieval, consistency, coverage, and update reliability", "query logs, graph topology, provenance, edit history, and benchmark tasks", "a rapid update or contradiction introduced into a dense subgraph", "constraint-memory terms do not improve error propagation or repair prediction", "milliseconds to decades; triples to knowledge ecosystems"),
    "B-10": P("sensor input, task demand, environmental change, and control goals", "actuation, compute, energy, uncertainty, and safety limits", "planning, replanning, fallback, learning, and human oversight", "learned policy, world model, event history, and accumulated wear", "task success, robustness, safety margin, and recovery", "simulator traces, field logs, interventions, near misses, and distribution shifts", "an out-of-distribution event during constrained operation", "the framework cannot separate robust adaptation from unsafe throughput", "milliseconds to decades; controllers to autonomous fleets"),
    "B-11": P("instructions, data, memory requests, and synchronization", "memory bandwidth, dependencies, energy, latency, and physical layout", "parallelism, caching, speculation, scheduling, and specialization", "architectural state, compiler choices, cache history, and accumulated heat", "throughput, latency, energy efficiency, and correctness", "hardware counters, traces, benchmarks, thermal data, and architecture simulations", "a memory-intensive workload under power or thermal limits", "the variables do not improve performance-portability or bottleneck prediction", "picoseconds to hardware generations; transistors to data centers"),
    "B-12": P("service demand across coupled engineered networks", "interdependent capacity, topology, maintenance, and control limits", "redundancy, control, repair, substitution, and coordinated recovery", "aging, technical debt, design lock-in, and prior failures", "resilience, cascade containment, service equity, and restoration", "cross-infrastructure telemetry, dependency maps, stress tests, and incident histories", "a common-cause shock across two engineered networks", "cross-network CDFD terms do not improve cascade or recovery prediction", "microseconds to decades; components to systems of systems"),
    "C-01": P("labor, ideas, capital, services, and opportunity seeking", "access, credit, discrimination, institutions, and geographic barriers", "mobility, training, enterprise, redistribution, and network support", "wealth, credentials, exclusion, policy, and family history", "income, mobility, participation, and opportunity distribution", "panel surveys, administrative records, labor flows, credit data, and network measures", "an economic shock or policy change applied across unequal starting conditions", "history-sensitive constraints do not improve mobility or opportunity forecasts", "months to generations; households to economies"),
    "C-02": P("payments, credit, liquidity, claims, and information", "capital, liquidity, collateral, trust, and counterparty limits", "clearing, market making, regulation, settlement, and emergency support", "leverage, losses, expectations, contracts, and crisis history", "credit availability, settlement, stability, and recovery", "balance sheets, transaction networks, spreads, defaults, and policy interventions", "a liquidity or collateral shock across a connected financial network", "the mapping adds no value beyond established balance-sheet and network models", "microseconds to decades; institutions to global finance"),
    "C-03": P("goods, services, capital, information, and contractual demand", "ports, tariffs, logistics, finance, and network dependencies", "substitution, inventory, rerouting, diplomacy, and production change", "contracts, specialization, infrastructure, and disruption history", "trade volume, shortages, prices, and recovery", "customs data, input-output tables, shipping traces, prices, and disruption records", "a corridor closure or supplier loss during high demand", "network memory does not improve shortage or trade-recovery prediction", "days to decades; firms to the world economy"),
    "C-04": P("people, remittances, information, risk, and opportunity gradients", "borders, cost, housing, jobs, rights, and social acceptance", "social networks, policy, integration, mobility, and mutual aid", "diaspora ties, path dependence, trauma, law, and settlement history", "movement, welfare, integration, and return or onward migration", "censuses, surveys, mobile data, remittances, policy changes, and migration histories", "a conflict, climate, or labor-market shock across different corridors", "the framework cannot improve explanation after established migration variables are included", "days to generations; households to transnational networks"),
    "C-05": P("people, resources, information, services, and economic activity", "land, housing, transport, utilities, governance, and inequality", "planning, infrastructure, markets, social networks, and mutual aid", "built form, segregation, investment, institutions, and prior shocks", "access, productivity, health, congestion, and resilience", "census, mobility, land-use, service, price, health, and budget records", "a population or hazard shock across unequal neighborhoods", "the mapping cannot identify differential access or recovery beyond urban baselines", "minutes to centuries; households to metropolitan systems"),
    "C-06": P("learners, knowledge, teaching time, attention, and credentials", "capacity, cost, prerequisites, language, access, and assessment", "pedagogy, support, peer learning, adaptive tools, and institutional change", "prior learning, curriculum, expectations, inequality, and institutional history", "mastery, retention, completion, mobility, and equity", "longitudinal learning data, attendance, assessments, interventions, and resource records", "a curriculum, staffing, or access change across different prior-learning states", "history-sensitive CDFD variables do not improve learning or completion prediction", "minutes to generations; classrooms to education systems"),
    "C-07": P("public demands, resources, information, authority, and collective action", "law, administration, legitimacy, coordination, and fiscal capacity", "deliberation, accountability, decentralization, learning, and emergency action", "precedent, bureaucracy, trust, institutional design, and crisis history", "service delivery, legitimacy, compliance, and adaptive capacity", "budgets, processing times, service outcomes, legal changes, surveys, and crisis responses", "an urgent public demand under contrasting institutional histories", "the framework cannot distinguish useful safeguards from harmful rigidity", "days to centuries; agencies to polities"),
    "C-08": P("population, economic activity, infrastructure use, and innovation", "land, networks, coordination, congestion, and resource limits", "agglomeration, specialization, infrastructure, and institutional adaptation", "built capital, network topology, inequality, and urban history", "scaling residuals, productivity, access, and environmental burden", "cross-city panels, infrastructure, emissions, mobility, patents, and welfare data", "a matched growth increment across cities with different inherited structures", "explicit constraint-memory terms do not explain residuals beyond scaling laws", "years to centuries; neighborhoods to city systems"),
    "C-09": P("economic, political, ecological, health, and information shocks", "fiscal, liquidity, institutional, social, and household buffers", "relief, coordination, substitution, learning, and collective action", "debt, trauma, distrust, depleted assets, and prior crises", "loss, unrest, contagion, recovery, and institutional change", "crisis chronologies, balance sheets, surveys, prices, policy actions, and recovery data", "a repeated shock before full social or economic recovery", "prior-crisis memory does not alter severity or recovery after present exposure is matched", "minutes to generations; households to international systems"),
    "C-10": P("human needs, capabilities, information, care, and economic activity", "ecological limits, institutions, inequality, violence, and exclusion", "cooperation, learning, redistribution, care, governance, and cultural change", "culture, wealth, trauma, law, technology, and historical path dependence", "flourishing, dignity, resilience, and intergenerational capability", "welfare panels, health, education, environmental, institutional, and inequality measures", "a shared shock across populations with contrasting capability and memory states", "the synthesis cannot improve multidimensional welfare or recovery analysis", "minutes to generations; persons to civilization-scale systems"),
    "D-01": P("sensory input, recurrent signaling, metabolic support, and task demand", "energy, attention, connectivity, inhibition, and integration limits", "plasticity, arousal, recurrent coordination, and compensatory recruitment", "learned priors, synaptic state, injury, sleep, and developmental history", "integration, reportability, performance, and recovery", "neurophysiology, imaging, perturbation, behavior, metabolic data, and longitudinal records", "a controlled perturbation of arousal, connectivity, or sensory load", "CDFD variables do not improve discrimination among competing consciousness models", "milliseconds to lifetimes; synapses to whole-brain networks"),
    "D-02": P("infection, contact, mobility, and pathogen replication", "susceptibility, immunity, behavior, healthcare, and surveillance capacity", "vaccination, behavior change, treatment, tracing, and system expansion", "immune history, trust, prior waves, infrastructure, and policy legacy", "incidence, severity, burden, spread, and recovery", "epidemiology, mobility, genomics, serology, healthcare load, and intervention records", "a variant or contact-rate shock across populations with different histories", "memory and capacity terms do not improve epidemic or health-system forecasts", "hours to decades; hosts to global transmission networks"),
    "D-03": P("tectonic stress, heat, fluids, sediment, and chemical gradients", "rock strength, friction, pressure, permeability, and geometry", "deformation, fracture, flow, phase change, and chemical alteration", "stratigraphy, faults, fabric, thermal state, and prior deformation", "landforms, hazards, material transport, and geological transition", "field mapping, geodesy, seismology, petrology, geochemistry, and stratigraphic records", "a stress or fluid-pressure perturbation across inherited structures", "explicit memory and topology do not improve geological interpretation or prediction", "seconds to billions of years; grains to planets"),
    "D-04": P("developmental signals, environmental exposures, hormones, and metabolism", "chromatin access, transcriptional capacity, repair, and cellular context", "remodeling, feedback, compensation, and lineage-specific regulation", "epigenetic marks, lineage, exposure history, and developmental timing", "gene expression, phenotype, persistence, and reversibility", "multi-omics, lineage tracing, perturbation, exposure cohorts, and longitudinal phenotypes", "a controlled exposure followed by removal or reprogramming", "past exposure does not alter response after current molecular state is controlled", "minutes to generations; loci to organisms"),
    "D-05": P("nutrients, metabolites, microbial migration, drugs, and host signals", "habitat, resources, competition, host immunity, and spatial structure", "community reassembly, functional redundancy, dispersal, and host regulation", "colonization, diet, antibiotics, infection, and host developmental history", "function, stability, metabolite flow, and recovery", "metagenomics, metabolomics, cultivation, diet and drug interventions, and longitudinal sampling", "an antibiotic or diet pulse followed by restoration", "structural memory does not improve functional or compositional recovery prediction", "minutes to lifetimes; molecules to host-associated ecosystems"),
    "D-06": P("coherent excitation, control signals, and environmental noise", "decoherence, dissipation, coupling, material boundaries, and measurement", "shielding, error correction, collective order, and driven control", "preparation history, defects, bath state, and prior measurement", "coherence, transport, phase stability, and response", "spectroscopy, coherence measurements, controlled baths, material characterization, and perturbation", "a calibrated increase in environmental coupling or disorder", "CDFD adds no measurable prediction beyond open-quantum-system theory", "femtoseconds to device lifetimes; excitations to macroscopic assemblies"),
    "D-07": P("orders, leverage, information, credit, and investor demand", "liquidity, market depth, capital, collateral, and network exposure", "price discovery, market making, hedging, intervention, and substitution", "positions, losses, expectations, rules, and crisis history", "volatility, liquidity, contagion, price formation, and recovery", "order books, trades, positions, funding data, networks, and interventions", "a liquidity or information shock under contrasting leverage histories", "the mapping adds no value beyond established microstructure and risk models", "microseconds to decades; venues to global markets"),
    "D-08": P("primary production, prey biomass, nutrients, and consumer demand", "stoichiometry, habitat, predation, competition, and spatial bottlenecks", "diet switching, migration, redundancy, storage, and population adjustment", "population structure, soil, disturbance, harvest, and evolutionary history", "trophic transfer, stability, cascades, and recovery", "food-web time series, isotope tracers, experiments, abundance, and productivity data", "consumer removal or resource pulse followed by recovery", "memory-aware terms do not improve trophic-cascade or recovery forecasts", "minutes to centuries; organisms to regional food webs"),
    "D-09": P("training data, gradients, context, and inference requests", "compute, memory, data quality, architecture, bandwidth, and evaluation", "optimization, routing, retrieval, tool use, and oversight", "weights, optimizer state, context, fine-tuning, and deployment feedback", "loss, capability, calibration, robustness, and reliability", "training curves, ablations, activations, evaluations, incidents, and distribution shifts", "a capacity bottleneck or distribution shift after training", "CDFD variables do not improve scaling, adaptation, or failure prediction", "nanoseconds to deployment lifetimes; parameters to AI ecosystems"),
    "D-10": P("messages, symbols, signals, and source entropy", "channel capacity, noise, attention, coding, and routing limits", "filtering, compression, coding, retransmission, and rerouting", "stored state, cache, prior information, protocol, and receiver history", "mutual information, error, delay, reach, and recovery", "channel measurements, traffic traces, coding experiments, network topology, and receiver behavior", "a noise or demand pulse across channels with different histories", "the mapping adds no explanatory value beyond information and queueing theory", "nanoseconds to centuries; channels to information ecosystems"),
    "D-11": P("orders, materials, cash, labor, and information", "supplier, transport, inventory, finance, and production capacity", "substitution, rerouting, buffering, prioritization, and coordination", "contracts, backlogs, inventories, trust, and disruption history", "fulfillment, shortage, cost, cascade size, and recovery", "firm transactions, shipment traces, inventories, supplier networks, and disruption histories", "a supplier or corridor failure under contrasting inventory histories", "memory and topology terms do not improve cascade or recovery prediction", "hours to decades; facilities to global supply networks"),
    "D-12": P("antigen, inflammatory signals, tissue damage, and metabolic demand", "immune, tissue, vascular, and metabolic capacity", "regulation, clearance, tolerance, repair, and memory response", "immune memory, scarring, chronic activation, and exposure history", "clearance, protection, collateral damage, and recovery", "immune profiling, clinical trajectories, perturbation, pathology, and longitudinal cohorts", "a repeated antigenic or inflammatory challenge", "history-sensitive terms do not improve protection or damage prediction beyond immunology baselines", "seconds to lifetimes; molecules to organisms"),
    "D-13": P("mutation, migration, selection, recombination, and reproduction", "population size, connectivity, resources, drift, and reproductive limits", "recombination, plasticity, dispersal, mate choice, and adaptation", "allele frequencies, bottlenecks, linkage, environment, and selection history", "diversity, adaptation, fixation, and extinction risk", "genomes, pedigrees, experimental evolution, demography, and environmental records", "a selection or migration shift across populations with different histories", "explicit memory and constraint variables do not improve evolutionary prediction", "generations to geological time; loci to metapopulations"),
    "E-01": P("domain-specific flows of energy, matter, information, organisms, capital, and force", "measured bottlenecks and finite capacities in each domain", "domain-specific adaptation, buffering, rerouting, repair, and control", "retained physical, biological, technical, institutional, or cognitive state", "overload, transition, recovery, and comparative transfer", "standardized domain datasets, perturbation records, null models, and runtime diagnostics", "matched perturbations across carefully normalized domain systems", "the shared architecture fails to improve prediction or comparison beyond domain baselines", "microseconds to geological time; local components to coupled global systems"),
    "F-01": P("nuclear energy generation, radiative transport, and mass flow", "gravity, opacity, fuel availability, and transport limits", "convection, expansion, fusion regulation, mass loss, and mixing", "composition, rotation, magnetic state, and prior burning stages", "luminosity, stability, nucleosynthesis, and evolutionary transition", "photometry, spectroscopy, asteroseismology, neutrinos, stellar populations, and models", "a comparison across stars of matched mass but different composition or rotation", "the CDFD translation adds no testable prediction beyond stellar structure and evolution", "seconds to billions of years; nuclei to stellar populations"),
    "F-02": P("accretion, star formation, radiation, gas flow, and angular momentum", "gravity, feedback, cooling, orbital structure, and halo potential", "spiral waves, bars, outflows, mixing, and orbital reorganization", "mergers, metallicity, stellar populations, and orbital history", "morphology, star formation, rotation, and long-term evolution", "multiwavelength surveys, kinematics, gas maps, stellar populations, and simulations", "a matched comparison across galaxies with contrasting merger or feedback histories", "the mapping adds no predictive value beyond standard galactic dynamics", "thousands to billions of years; clouds to galaxy clusters"),
    "F-03": P("mass, energy, angular momentum, magnetic flux, and accretion", "horizon geometry, gravity, radiative efficiency, and disk transport", "disk reconfiguration, jets, outflows, and environmental feedback", "spin, charge, growth, magnetic topology, and accretion history", "luminosity, growth, jet power, and thermodynamic accounting", "gravitational waves, spectra, timing, imaging, accretion estimates, and simulations", "an accretion-state transition at matched mass and environment", "CDFD introduces no distinguishable prediction beyond relativity and accretion physics", "microseconds to cosmic time; horizons to galactic environments"),
    "F-04": P("particle, energy, and reaction fluxes", "binding, conservation laws, Coulomb barriers, and available states", "decay, reaction channels, collective modes, and energy redistribution", "isotopic composition, excitation, deformation, and reaction history", "stability, yields, decay pathways, and energy release", "cross sections, decay data, spectroscopy, collision experiments, and nuclear models", "a controlled energy or particle-flux scan across isotopes", "the translation adds no testable structure beyond established nuclear theory", "attoseconds to geological time; nucleons to astrophysical reaction networks"),
    "F-05": P("particles, heat, current, radiation, and momentum", "fields, collisions, geometry, confinement, and transport barriers", "waves, reconnection, turbulence, control, and profile adjustment", "magnetic topology, distribution functions, impurities, and prior events", "confinement, heating, instability, transport, and recovery", "laboratory diagnostics, solar observations, in-situ spacecraft data, and simulations", "a controlled heating, current, or magnetic-topology perturbation", "CDFD variables do not improve instability or confinement prediction beyond plasma models", "nanoseconds to solar cycles; kinetic scales to astrophysical plasmas"),
    "G-01": P("utterances, meanings, learners, media, and social interaction", "cognition, channel capacity, social structure, ambiguity, and convention", "innovation, repair, learning, borrowing, and accommodation", "grammar, lexicon, corpora, identity, institutions, and historical contact", "intelligibility, change, diffusion, and linguistic diversity", "corpora, experiments, social networks, historical records, and longitudinal language data", "a communication or contact shift across communities with different histories", "constraint-memory terms do not improve language-change or comprehension prediction", "milliseconds to millennia; speakers to language families"),
    "G-02": P("observations, anomalies, ideas, instruments, and research effort", "methods, evidence, institutions, incentives, and cognitive limits", "replication, theory revision, tool building, collaboration, and critique", "paradigms, training, citation networks, instruments, and institutional history", "explanation, prediction, error correction, and scientific transition", "publication and citation networks, replications, forecasts, funding, and historical case studies", "a persistent anomaly or new instrument introduced into contrasting fields", "the mapping cannot distinguish productive stability from obstructive lock-in", "months to centuries; projects to scientific institutions"),
    "G-03": P("data, compute, models, feedback, deployment demand, and social attention", "compute, data quality, governance, evaluation, energy, and oversight", "learning, tool use, modularity, monitoring, correction, and institutional response", "weights, deployed systems, standards, incidents, incentives, and feedback history", "capability, reliability, diffusion, risk, and social adaptation", "scaling records, evaluations, deployment telemetry, incidents, policy changes, and energy use", "a capability or deployment shock under contrasting oversight histories", "CDFD variables do not improve capability, failure, or governance-response prediction", "microseconds to decades; model components to socio-technical ecosystems"),
}


PART_CONTEXT: dict[str, tuple[str, str, str]] = {
    "A": (
        "Earth systems",
        "the universal comparison is between coupled transport, finite environmental capacity, buffering, and retained landscape or ecosystem state. Universality here cannot erase conservation laws, geometry, or scale; it must expose where those domain equations create comparable overload and recovery structures.",
        r"\cite{Holling1973,Turing1952,BakTangWiesenfeld1987}",
    ),
    "B": (
        "engineered systems",
        "the universal comparison is between demand, designed capacity, feedback control, dependency topology, and accumulated technical state. The strongest engineering use is prospective: the mapping must identify a bottleneck, a control action, or a recovery signature before the failure occurs.",
        r"\cite{BarabasiAlbert1999,WattsStrogatz1998,Shannon1948,BakTangWiesenfeld1987}",
    ),
    "C": (
        "socioeconomic systems",
        "the universal comparison is between human and institutional throughput, unequal access to capacity, adaptive coordination, and historical path dependence. The variables are not morally neutral: aggregation can hide who receives flow, who bears constraint, and whose prior losses become persistent memory.",
        r"\cite{BarabasiAlbert1999,WattsStrogatz1998,Holling1973,Shannon1948}",
    ),
    "D": (
        "domain applications",
        "the universal comparison is a disciplined translation test across systems with very different material mechanisms. A valid mapping preserves the baseline science of the domain, declares the scale of every variable, and earns its place through a discriminating prediction rather than resemblance alone.",
        r"\cite{Holling1973,Turing1952,Shannon1948,BakTangWiesenfeld1987}",
    ),
    "E": (
        "universal synthesis",
        "the universal object is not a substance or a single physical mechanism. It is a candidate model architecture: driven flow meets finite constraint, response changes effective capacity, and retained state changes later trajectories. The architecture survives only where normalization and comparison remain meaningful.",
        r"\cite{BarabasiAlbert1999,WattsStrogatz1998,Holling1973,Turing1952,Shannon1948,BakTangWiesenfeld1987}",
    ),
    "F": (
        "cosmic and subatomic systems",
        "the universal comparison must remain subordinate to conservation laws, relativity, quantum mechanics, and established astrophysical or plasma equations. CDFD is useful only if it compresses a regime transition or hysteresis question without pretending that biological adaptation and physical response are the same mechanism.",
        r"\cite{Turing1952,Shannon1948,BakTangWiesenfeld1987}",
    ),
    "G": (
        "abstract and cognitive systems",
        "the universal comparison is between information-bearing activity, limited channels or institutions, adaptive reorganization, and retained semantic or technical structure. Because meanings and goals are not conserved physical quantities, every mapping must state its observational unit and avoid treating metaphor as measurement.",
        r"\cite{Shannon1948,BarabasiAlbert1999,WattsStrogatz1998,Turing1952,BakTangWiesenfeld1987}",
    ),
}


TITLE_OVERRIDES = {
    "A-01": "Earth Unified Environmental Transport",
    "B-01": "Unified Infrastructure",
    "B-08": "Cloud Systems",
    "B-10": "Autonomous Systems",
    "B-12": "Engineering Synthesis",
    "C-01": "Economics and Opportunity",
    "C-09": "Socioeconomic Crises",
    "D-02": "Pandemic Dynamics",
    "D-06": "Macroscopic Quantum Systems",
    "D-08": "Ecology and Trophic Systems",
    "E-01": "Universal AFL Synthesis",
}

GENERIC_ABSTRACT_INTRO = (
    "This paper asks whether Constraint-Driven Flux Dynamics (CDFD) and Adaptive "
    "Flux Limitation (AFL) can give the named system a sharper audit language. "
    "The working variables are driving flux $\\Phi$, constraint $C$, surface "
    "responsiveness $S$, and structural memory $M_s$. The useful question is "
    "plain: what can be measured, what would count as overload, and what result "
    "would make the mapping fail?\n"
)

DATA_AVAILABILITY = r"""\section*{Data Availability}
Part-specific runtime diagnostics are under each Part's \path{outputs/} directory.

Release-wide code: \path{Part_E_Synthesis/supplementary/}.

Generated summaries: \path{Part_E_Synthesis/outputs/}.

Figures: \path{Part_E_Synthesis/figures/}."""

CLAIM_REPLACEMENTS = {
    "catastrophic catastrophic": "catastrophic",
    "the exact same mathematical laws": "a comparable normalized flow--constraint architecture",
    "the exact same physical mechanisms": "a comparable high-level constraint architecture",
    "the exact same physical logic": "a comparable flow-control logic",
    "the exact same transport topology": "a comparable transport topology",
    "the exact same thermodynamic boundaries": "comparable finite-capacity boundaries",
    "the exact same topological mathematics": "a comparable flow--constraint architecture",
    "the exact same": "a comparable",
    "in the exact same manner": "in a comparable but materially distinct manner",
    "entirely isomorphic to": "formally comparable at the declared-variable level to",
    "mathematically identical to": "structurally analogous under this mapping to",
    "mathematically indistinguishable from": "formally comparable at the declared-variable level to",
    "mathematically doomed to": "predicted here to be vulnerable to",
    "mathematically incapable of": "potentially unable to",
    "mathematically demonstrate that": "form the testable hypothesis that",
    "mathematically necessitates": "can drive",
    "the ultimate cause of": "a candidate contributor to",
    "leading invariably to": "which may contribute to",
    "the universal mathematical threshold": "a candidate measurable boundary",
    "systemic collapse becomes inevitable": "systemic collapse risk rises",
    "permanently neutralized": "reduced under the declared conditions",
    "entirely captured by": "summarized provisionally by",
    "entirely dictated by": "potentially shaped by",
    "a universal mathematical attractor state": "a candidate normalized operating regime",
    "proving that": "supporting the testable hypothesis that",
    "Because the environment inside the pocket is perfectly isolated from the macroscopic flux, decoherence is delayed.": "Because the structured environment can partially shield and tune coupling to the surrounding bath, coherence may persist longer than an unstructured comparison permits.",
    "experiments reveal that photosynthetic complexes transfer energy with near-100\\% efficiency by exploiting quantum coherence, exploring multiple energy pathways simultaneously.": "experiments motivate active study of high-efficiency excitation transfer and the possible role of transient quantum coherence in photosynthetic complexes.",
    "Just as a dam will eventually burst if the reservoir overfills without a spillway, a border constraint will inevitably suffer topological rupture if it attempts to infinitely block a massive survival-driven flux.": "A border system that lacks lawful, humane response capacity may experience abrupt route changes or institutional stress under sustained survival-driven movement; the threshold and outcome are empirical questions.",
    "Hydrology is the macroscopic study of fluid problem-solving. By framing riverine evolution within CDFD, we mathematically equate the branching of a river delta to the branching of a neural network or a lightning strike. The Earth's surface dynamically resculpts its own constraints to ensure that thermodynamic flux is always processed at optimal criticality.": "Hydrology provides a direct test of flow interacting with a surface that the flow itself modifies. CDFD makes river branching comparable to other adaptive transport networks at the level of measurable topology, while the governing hydrological mechanisms remain domain specific.",
    "The fate of human civilization is not a matter of politics; it is a matter of constraint-based modelling. CDFD suggests that no active surface can permanently sustain a $\\Psi_s \\gg 1$ over-flux regime against a fixed planetary constraint. Humanity must intentionally restructure its global topological memory, or the laws of thermodynamics will violently restructure it for us.": "Human futures depend on politics, institutions, technology, ecology, and physical limits together. CDFD contributes a testable constraint-based account of how persistent over-load and inherited structure may narrow the available response space.",
    "Macroscopic quantum coherence in biology is the ultimate triumph of topological constraint engineering. By applying CDFD, we see that living organisms natively utilize a comparable high-level constraint architecture to isolate a delicate quantum superposition as they do to isolate a vital organ from a deadly pathogen. The geometry of the protein scaffold serves as a universal constraint barrier, mathematically firewalling the quantum realm from thermodynamic collapse.": "Macroscopic and biological quantum systems provide a stringent boundary test for CDFD. The useful claim is limited: structured environments may alter coupling, transport, and coherence lifetimes, and the CDFD variables must add a discriminating prediction beyond open-quantum-system theory.",
    "Therefore, the only mathematically valid way to improve human well-being and complexity is to increase $S$ (technological and social efficiency).": "One candidate route to improve human well-being without raising physical throughput is to increase $S$ through technological, social, and institutional efficiency.",
    "As measurement tools improve, anomalous data ($\\Phi$) inevitably skyrockets. The current paradigm cannot process this flux natively. In an attempt to save the theory, the establishment introduces ad-hoc corrections (epicycles), effectively driving up the constraint complexity ($C$). Because the institutional memory ($M_s$) is absolute, the system refuses to adapt smoothly.": "As measurement tools improve, anomalous data ($\\Phi$) can accumulate faster than a prevailing framework can absorb it. Ad-hoc corrections may raise effective constraint complexity ($C$), while institutional memory ($M_s$) can slow revision; whether this produces productive refinement or rigid lock-in is testable.",
    "Scaling laws are not empirical coincidences; they are the fundamental shadow of CDFD mathematics. Whether a system scales sublinearly to survive biological constraints or superlinearly to exploit informational density, it is potentially shaped by the continuous topological effort to maintain the critical $\\Psi_s \\approx 1$ equilibrium.": "Scaling laws are empirical regularities that provide a demanding test for CDFD. The framework is useful only if its constraint, response, and memory variables explain held-out scaling residuals better than established models.",
    "Education is an informational fluid dynamics problem. Institutional tradition is structural memory, and bureaucratic standardization is topological friction. By applying CDFD to pedagogy, we form the testable hypothesis that over-constraining the learning process inevitably strangles societal advancement, necessitating violent systemic resets to restore informational liquidity.": "Education can be studied as constrained knowledge transfer with strong institutional memory. The CDFD hypothesis is that some forms of over-constraint reduce learning and adaptation; the test is whether the declared variables improve prediction without treating reform or disruption as inevitable.",
    "When a language spreads across a vast geographic area, it invariably encounters friction. Populations separate, isolating groups and limiting communication. Over time, dialects form, eventually diverging into entirely separate languages. While sociolinguistics attributes this to cultural drift, CDFD models it as the inevitable topological breakdown of an over-constrained flux network.": "When a language spreads across a wide geographic and social space, changing contact networks can limit communication and support dialect formation. CDFD treats this as a testable interaction among information flow, network constraint, adaptive repair, and historical memory rather than an inevitable breakdown.",
    "Artificial Intelligence is bound by a comparable thermodynamic and topological limits as biological metabolism and galactic formation. By treating deep learning through the lens of Adaptive Flux Limitation, we identify the mathematical ceiling of static neural scaling and outline the required structural dynamics for genuine, open-ended machine cognition.": "Artificial-intelligence systems face measurable limits in compute, data, energy, evaluation, and governance. CDFD offers a candidate architecture for testing how those constraints interact with learning and deployment history; it does not establish a universal ceiling or guarantee open-ended cognition.",
    "Black hole thermodynamics is formally comparable at the declared-variable level to the constraint-flow dynamics observed in living biological systems. An event horizon is an active biological-like membrane for the cosmos: it accretes information, encodes it into structural memory, and actively radiates energy to prevent catastrophic thermodynamic stagnation. The holographic principle is merely the memory term $M_s$ operating at the Planck limit.": "Black-hole thermodynamics and living systems can both be described with boundary, flux, and retained-state variables, but their mechanisms are not isomorphic. This paper limits the comparison to measurable accretion, horizon, spin, and radiation quantities and asks whether the CDFD translation adds anything beyond relativity and accretion physics.",
    "Magnetic reconnection is not an isolated electromagnetic anomaly. It is the plasma-equivalent of cellular apoptosis or market collapse---a violent shedding of chronic constraint to restore the healthy $\\Psi_s \\approx 1$ flow regime. By analyzing plasmas through the CDFD ontology, we frame the hypothesis that the rules governing the sun's corona are structurally analogous under this mapping to the adaptive scaling rules governing human physiology and universal topology.": "Magnetic reconnection is a plasma process governed by field topology, kinetic effects, and dissipation. CDFD supplies a candidate regime-change description whose value depends on improving prediction of reconnection, transport, or recovery without equating plasma mechanisms to biological or market failure.",
    "CDFD provides the universal mathematics to describe this coupling. The laws governing the flow of cars on a highway are structurally identical to the laws governing the flow of packets in a router or blood in a vein.": "CDFD provides a common audit language for this coupling. Traffic, packet routing, and blood flow have different governing mechanisms, but each can be tested for measurable bottlenecks, network dependence, overload, and recovery.",
    "The adaptive ratio crashes to $\\Psi_s \\ll 1$. The node begins \"thrashing\" (constantly swapping memory to disk), which drops its effective throughput to near zero. Because distributed tasks often require synchronous completion, the entire cluster stalls waiting for the deadlocked node. This is a topological blockage identical to a blood clot causing a systemic stroke.": "The adaptive ratio drops to $\\Psi_s \\ll 1$. The node begins \"thrashing\" (constantly swapping memory to disk), which reduces effective throughput. Because distributed tasks often require synchronous completion, the cluster can stall while waiting for the constrained node. The medical analogy is only structural: the engineering claim must be tested with queue, memory, and dependency telemetry.",
    "The system enters a $\\Psi_s \\ll 1$ bottleneck ($\\Psi_s > 1$ lock state). API requests time out. The cloud application suffers an ischemic failure due to a topological memory lock, identical to a biological stroke.": "The system enters a bottleneck or lock state and API requests time out. CDFD treats this as a measurable interaction among demand, database capacity, statefulness, and scaling response; no biological identity is implied.",
    "Without memory, the soil's effective responsiveness $S$ drops. When heavy rain (a spike in $\\Phi$) hits the soil, the system cannot absorb or route the fluid. The adaptive ratio crashes ($\\Psi_s \\ll 1$). The flux simply runs off the surface, taking the remaining loose topsoil with it. This is \\textbf{Desertification}---the total topological failure of an active membrane, identical in mathematics to an ischemic organ failing due to blocked arterial constraints.": "When root, pore, and fungal structure are damaged, effective responsiveness $S$ may fall. Under heavy rain, reduced infiltration can increase runoff and erosion. The CDFD claim is limited to a measurable history-dependent soil response; comparison with an ischemic organ is an analogy, not a shared material mechanism.",
    "Whether analyzing the branching of a mammalian cardiovascular system or the layout of an electrical power grid, complex systems exhibit identical geometric architectures. As they grow in size, their internal transport networks branch fractally. This fractal branching ensures that energy and resources reach every localized node.\n\nIn CDFD, this geometry is not accidental. It is the physical manifestation of the system attempting to regulate its internal thermodynamic pressure. The scaling laws are simply the mathematical boundaries of this topological optimization.": "Cardiovascular and electrical-grid networks can exhibit partly comparable branching or connectivity statistics, but their architectures, objectives, and governing mechanisms differ. CDFD therefore treats scaling as a discriminating empirical test: declared constraint and memory variables must explain held-out residuals beyond established network and scaling models.",
    "Migration is not a political choice; it is a thermodynamic imperative. Sovereign borders are artificial topological constraints placed upon a natural fluid flow. By analyzing migration through the CDFD ontology, we model the hypothesis that rigid, uncompromising border policies increase the risk of localized systemic collapse. Sustainable geopolitics requires elastic responsiveness ($S$) to manage the inevitable flow of human survival.": "Migration is shaped by safety, opportunity, rights, policy, cost, social networks, and individual agency. CDFD offers a candidate model of how corridor capacity and institutional response affect movement and welfare; it does not reduce people to fluid or make a policy outcome thermodynamically inevitable.",
    "Epigenetics is the molecular implementation of thermodynamic memory. By reframing chromatin remodeling within the CDFD ontology, we erase the conceptual gap between macroscopic trauma and molecular biology. The cell regulates its transcriptional throughput using the identical physical principles that an economy uses to regulate capital flow during a recession.": "Epigenetic state is a concrete molecular form of biological memory whose mechanisms must be studied on their own terms. CDFD supplies a high-level language for testing history-dependent constraint and response, but it does not erase the mechanistic gap between chromatin regulation, trauma, and economic systems.",
    "Biodiversity is not simply a catalog of species; it is the mathematical parameter $S$ that keeps the Earth's biological surface elastically robust against constraint shocks. Using CDFD, we model the hypothesis that replacing complex ecosystems with low-diversity systems guarantees catastrophic topological failure the moment external stabilization forces are removed.": "Biodiversity can contribute to response diversity, redundancy, and recovery, but it cannot be reduced to a single universal parameter. The CDFD hypothesis is that lower diversity can reduce measured responsiveness under specified shocks; the claim fails where low-diversity systems remain robust after confounders are controlled.",
    "Ocean currents are a natural test case for flow, constraint, response, and memory. CDFD/AFL is useful here only as a disciplined measurement language. The release-level claim remains limited to that role.": "Ocean-current observations provide a direct test of flow, constraint, response, and memory. The CDFD and AFL framing is useful here only as a disciplined measurement language, and the release-level claim remains limited to that role.",
    "Ocean currents are a natural test case for flow, constraint, response, and\nmemory. CDFD/AFL is useful here only as a disciplined measurement language. The\nrelease-level claim remains limited to that role.": "Ocean-current observations provide a direct test of flow, constraint, response, and memory. The CDFD and AFL framing is useful here only as a disciplined measurement language, and the release-level claim remains limited to that role.",
    r"The diagnostic script \path{Part_E_Synthesis/supplementary/run_partiv_discovery.py}": "The release-local discovery script",
    r"The diagnostic script \texttt{Part\_E\_Synthesis/supplementary/run\_partiv\_discovery.py}": "The release-local discovery script",
    r"The Part B rows in \texttt{Part\_B\_Engineered\_Systems/outputs/domain\_adapter\_sweep.csv}": "The Part B output slice",
    r"""    \item \textbf{Induced seismicity}: maximum induced earthquake magnitude scales as $\log_{10}
          M_0 \propto \log_{10}(V_{inject}/\sqrt{C_{friction}})$ where $V_{inject}$ is injection
          volume; AFL predicts magnitude ceiling from permeability and injection parameters;""": r"""    \item \textbf{Induced seismicity}: test a candidate relation between injected volume,
          mapped fault constraint, and maximum observed moment:
          \[
          \log_{10} M_0 \propto \log_{10}\left(V_{inject}/\sqrt{C_{friction}}\right).
          \]
          The relation must be compared with established induced-seismicity models;""",
    r"\texttt{Part\_E\_Synthesis/supplementary/run\_partiv\_discovery.py}": r"\path{Part_E_Synthesis/supplementary/run_partiv_discovery.py}",
    r"\texttt{Part\_E\_Synthesis/supplementary/}": r"\path{Part_E_Synthesis/supplementary/}",
    r"\texttt{Part\_E\_Synthesis/outputs/}": r"\path{Part_E_Synthesis/outputs/}",
    r"\texttt{Part\_E\_Synthesis/figures/}": r"\path{Part_E_Synthesis/figures/}",
}


def tex_files() -> list[Path]:
    return sorted(RELEASE_ROOT.glob("Part_*/papers/*.tex"))


def paper_label(path: Path) -> str:
    part_name = path.relative_to(RELEASE_ROOT).parts[0]
    match = re.match(r"Part_([A-G])_", part_name)
    if match is None:
        raise ValueError(f"Cannot identify Part letter for {path}")
    number = int(path.stem.split("_", 1)[0])
    return f"{match.group(1)}-{number:02d}"


def paper_title(path: Path, label: str) -> str:
    if label in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[label]
    words = path.stem.split("_")[1:]
    if words and words[0] in {"Earth", "Eng", "Soc", "Dom", "Cosmos", "Physics", "Abs"}:
        if words[0] != "Earth":
            words = words[1:]
    acronyms = {"Ai": "AI", "Afl": "AFL"}
    return " ".join(acronyms.get(word, word) for word in words)


def latex_escape(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
    }
    return "".join(replacements.get(char, char) for char in text)


def short_label(text: str, limit: int = 58) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rsplit(" ", 1)[0] + "..."


def ensure_packages(text: str) -> str:
    additions: list[str] = []
    if r"\usepackage{tikz}" not in text:
        additions.append(r"\usepackage{tikz}")
        additions.append(r"\usetikzlibrary{arrows.meta,positioning}")
    if r"\usepackage{tabularx}" not in text:
        additions.append(r"\usepackage{tabularx}")
    if not additions:
        return text
    return re.sub(
        r"(\\documentclass(?:\[[^\]]*\])?\{[^}]+\}\s*)",
        lambda match: match.group(1) + "\n".join(additions) + "\n",
        text,
        count=1,
    )


def upgraded_abstract(title: str, profile: Profile) -> str:
    return (
        r"\begin{abstract}" + "\n"
        f"This paper develops a falsifiable CDFD/AFL model of {latex_escape(title)}. "
        f"It maps {latex_escape(profile.drive)} to driving flux $\\Phi$, "
        f"{latex_escape(profile.constraint)} to active constraint $C$, "
        f"{latex_escape(profile.response)} to responsiveness $S$, and "
        f"{latex_escape(profile.memory)} to structural memory $M_s$. "
        f"The target outcome is {latex_escape(profile.outcome)}, tested against "
        f"{latex_escape(profile.evidence)}. The paper treats universality as a shared "
        "model architecture rather than an assertion that unlike systems have the "
        "same material mechanism. It states the negative result that would make the "
        "mapping unnecessary and places the domain claim inside the cumulative CDFD "
        "programme and its reproducible runtime boundary."
        "\n" + r"\end{abstract}"
    )


def replace_generic_abstract(text: str, title: str, profile: Profile) -> str:
    pattern = re.compile(
        r"\\begin\{abstract\}\s*"
        r"This paper asks whether Constraint-Driven Flux Dynamics \(CDFD\) and Adaptive Flux Limitation \(AFL\) "
        r"can give the named system a sharper audit language\..*?"
        r"what result would make the mapping fail\?\s*"
        r"\\end\{abstract\}",
        flags=re.S,
    )
    text = pattern.sub(lambda _match: upgraded_abstract(title, profile), text, count=1)
    return text.replace(GENERIC_ABSTRACT_INTRO, "")


def discipline_claims(text: str) -> str:
    for old, new in CLAIM_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def normalize_data_availability(text: str) -> str:
    return re.sub(
        r"\\section\*\{Data Availability\}.*?"
        r"(?=\n\\section\{Reference Layer\}|\n\\bibliographystyle|\Z)",
        lambda _match: DATA_AVAILABILITY + "\n\n",
        text,
        count=1,
        flags=re.S,
    )


def normalize_legacy_tables(text: str) -> str:
    layouts = {
        "lll": r"@{}lXX@{}",
        "lllll": r"@{}lXXXX@{}",
    }
    for columns, layout in layouts.items():
        pattern = re.compile(
            rf"\\begin\{{tabular\}}\{{{columns}\}}(.*?)\\end\{{tabular\}}",
            flags=re.S,
        )
        text = pattern.sub(
            lambda match, layout=layout: (
                rf"\begin{{tabularx}}{{\textwidth}}{{{layout}}}"
                + match.group(1)
                + r"\end{tabularx}"
            ),
            text,
        )
    return text


def diagram(label: str, title: str, profile: Profile) -> str:
    node_drive = latex_escape(short_label(profile.drive))
    node_constraint = latex_escape(short_label(profile.constraint))
    node_response = latex_escape(short_label(profile.response))
    node_outcome = latex_escape(short_label(profile.outcome))
    node_memory = latex_escape(short_label(profile.memory))
    figure_label = label.lower().replace("-", "")
    return rf"""
\begin{{figure}}[htbp]
\centering
\begin{{tikzpicture}}[
    node distance=0.48cm,
    every node/.style={{font=\small}},
    box/.style={{draw, rounded corners, align=center, minimum height=1.45cm, text width=3.0cm, fill=blue!6}},
    memory/.style={{draw, rounded corners, align=center, minimum height=1.25cm, text width=3.4cm, fill=orange!12}},
    flow/.style={{-{{Latex[length=2.2mm]}}, thick}},
    feedback/.style={{-{{Latex[length=2.2mm]}}, thick, dashed}}
]
\node[box] (drive) {{\textbf{{Drive $\Phi$}}\\\scriptsize {node_drive}}};
\node[box, right=of drive] (constraint) {{\textbf{{Constraint $C$}}\\\scriptsize {node_constraint}}};
\node[box, right=of constraint] (response) {{\textbf{{Response $S$}}\\\scriptsize {node_response}}};
\node[box, right=of response] (outcome) {{\textbf{{Observed outcome}}\\\scriptsize {node_outcome}}};
\node[memory, below=0.72cm of constraint] (memory) {{\textbf{{Structural memory $M_s$}}\\\scriptsize {node_memory}}};
\draw[flow] (drive) -- (constraint);
\draw[flow] (constraint) -- (response);
\draw[flow] (response) -- (outcome);
\draw[feedback] (outcome.south) |- (memory.east);
\draw[feedback] (memory.north) -- (constraint.south);
\end{{tikzpicture}}
\caption{{Paper {label} observable CDFD/AFL architecture for {latex_escape(title)}. Solid arrows give the proposed forward chain; dashed arrows make history-dependent feedback explicit.}}
\label{{fig:{figure_label}-architecture}}
\end{{figure}}
""".strip()


def synthesis_figures(label: str) -> str:
    if label != "E-01":
        return ""
    return r"""
\begin{figure}[htbp]
\centering
\includegraphics[width=0.96\textwidth]{Part_E_Synthesis/figures/universal_cascade.png}
\caption{Release-local universal cascade stress test generated by the current CDFD Runtime. The figure is a numerical diagnostic, not field validation of a domain claim.}
\label{fig:e01-runtime-cascade}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.96\textwidth]{Part_E_Synthesis/figures/domain_sweep_psi.png}
\caption{Selected-domain adapter sweep generated from the release-local Part IV discovery pass. Differences show the declared adapter parameterization and provide targets for later calibration.}
\label{fig:e01-domain-sweep}
\end{figure}
""".strip()


def upgrade_block(label: str, title: str, profile: Profile) -> str:
    part = label[0]
    context_name, context_text, external_citations = PART_CONTEXT[part]
    e = latex_escape
    block = rf"""
{BEGIN_MARKER}
\section{{Major Universal Upgrade: Mechanism, Scale, and Tests}}

\subsection{{Observable Translation}}

The paper-specific translation begins with an observable chain rather than a
verbal analogy. For {e(title)}, the proposed drive is {e(profile.drive)}.
The active limitation is {e(profile.constraint)}. Responsiveness is carried by
{e(profile.response)}, while retained state is represented by
{e(profile.memory)}. The outcome to explain is {e(profile.outcome)}.

\begin{{table}}[htbp]
\centering
\small
\caption{{Operational CDFD/AFL map for Paper {label}.}}
\begin{{tabularx}}{{\textwidth}}{{|l|X|X|}}
\hline
\textbf{{Term}} & \textbf{{Paper-specific observable meaning}} & \textbf{{Measurement question}} \\
\hline
$\Phi$ & {e(profile.drive)} & What rate, load, gradient, or demand enters the focal system? \\
\hline
$C$ & {e(profile.constraint)} & Which measured bottleneck limits transfer, function, or recovery? \\
\hline
$S$ & {e(profile.response)} & Which process changes effective capacity or reroutes the load? \\
\hline
$M_s$ & {e(profile.memory)} & Which retained state makes equal present loads produce different futures? \\
\hline
$Y$ & {e(profile.outcome)} & Which outcome is predicted out of sample, with uncertainty? \\
\hline
\end{{tabularx}}
\end{{table}}

{diagram(label, title, profile)}

\subsection{{Minimal Coupled Model}}

A paper-level model must separate throughput, constraint accumulation, response,
and history. One deliberately minimal form is
\begin{{align}}
Y(t) &= \frac{{\Phi(t)S(t)}}{{\epsilon + C(t)}}, \\
\frac{{dC}}{{dt}} &= \alpha \Phi(t) - \beta S(t)C(t) + \gamma \mathcal{{L}}C(t), \\
\frac{{dM_s}}{{dt}} &= \eta C(t) - \mu M_s(t), \\
\Psi_s(t) &= \frac{{\widehat{{\Phi}}(t)}}{{\epsilon+\widehat{{C}}(t)}}\,
             \widehat{{S}}(t)\,[1+\omega\widehat{{M_s}}(t)] .
\end{{align}}
Here $Y$ is the measured output, $\epsilon>0$ prevents a singular denominator,
$\mathcal{{L}}$ is a spatial or network coupling operator, and hats denote
explicitly normalized variables. The sign and magnitude of $\omega$ must be
estimated: memory can preserve useful organization or amplify damage. No fixed
threshold is universal before the variables, normalization, and observation
scale are declared.

For this paper, the hypothesized causal sequence is specific. A change in
{e(profile.drive)} arrives faster than {e(profile.response)} can compensate.
This raises or redistributes {e(profile.constraint)}. If the load persists,
the retained state encoded by {e(profile.memory)} changes the next response, so a later event of equal
magnitude can produce a different trajectory in {e(profile.outcome)}. The
scientific task is to estimate that sequence against the best ordinary model of
the domain, not merely to redescribe the outcome after it occurs.

\subsection{{Cross-Scale Universality Without Mechanistic Erasure}}

For the {context_name} family, {context_text} {external_citations}
The CDFD programme is cumulative: Part I supplies the flow--constraint
foundation \cite{{MujjabiPartI2026}}; Part II asks when maintained throughput
supports persistent organized states \cite{{MujjabiPartII2026}}; Part III
develops adaptive limitation and biological memory \cite{{MujjabiPartIII2026}};
and Part IV \cite{{MujjabiPartIV2026}} tests how much of that architecture
survives translation. The CDFD Runtime \cite{{CDFDRuntime2026}} supplies a
reproducible numerical stress surface, but it does not substitute for the
domain evidence named here.

The required scale declaration for this paper is {e(profile.scale)}. At short
scales, the key question is whether the incoming drive is transmitted,
buffered, or diverted. At intermediate scales, response changes effective
capacity and network exposure. At long scales, retained structure can alter the
state space itself. A result is genuinely cross-scale only when the aggregation
rule is stated and the same conclusion is not an artifact of averaging.

\subsection{{Evidence Ladder and Discriminating Tests}}

\begin{{table}}[htbp]
\centering
\small
\caption{{Evidence ladder for Paper {label}. Each rung can fail independently.}}
\begin{{tabularx}}{{\textwidth}}{{|p{{0.17\textwidth}}|X|X|}}
\hline
\textbf{{Test}} & \textbf{{Design}} & \textbf{{Discriminating result}} \\
\hline
Proxy audit & Measure {e(profile.evidence)} and preregister how each record maps to $\Phi$, $C$, $S$, $M_s$, and $Y$. & The mapping fails if proxies are non-identifiable, circular, or change meaning across cases. \\
\hline
Load ramp & Apply or observe {e(profile.stress)} while estimating the dominant constraint and response time. & A threshold claim requires a reproducible nonlinear change and uncertainty bounds, not a visually chosen breakpoint. \\
\hline
Recovery and memory & Match present load across units with different histories, then compare recovery paths. & The memory claim requires history-dependent divergence after current conditions are controlled. \\
\hline
Model comparison & Compare the baseline domain model with and without the CDFD/AFL state variables using held-out data. & The paper's stated falsifier is: {e(profile.falsifier)}. \\
\hline
\end{{tabularx}}
\end{{table}}

The strongest practical design combines a prospective perturbation with a
recovery window. The load-ramp phase estimates where constraint begins to rise
faster than output. The recovery phase estimates $\beta$ and $\mu$, separating
fast relaxation from persistent memory. A topology or coupling intervention
then asks whether rerouting changes the cascade as predicted. Null results are
informative because they identify domains in which the universal notation adds
no measurable value.

\subsection{{Research Programme and Boundary Conditions}}

The immediate research programme has four steps. First, construct a documented
dataset from {e(profile.evidence)} and retain raw units before normalization.
Second, fit a baseline domain model and report its calibration and out-of-sample
error. Third, add the smallest identifiable CDFD/AFL state extension and test
whether it improves prediction of {e(profile.outcome)}. Fourth, repeat the
analysis across the declared scale range and publish negative cases as part of
the universality audit.

Three boundaries are non-negotiable. Correlation between flow and failure does
not identify a constraint mechanism. A fitted memory term does not prove that
the stored state has the same material meaning in another domain. Finally, a
runtime cascade is evidence about the implementation, not evidence that the
real system follows it. The paper becomes stronger when it can say precisely
where the translation stops.

{synthesis_figures(label)}
{END_MARKER}
""".strip()
    return block + "\n"


def insert_or_replace_upgrade(text: str, block: str) -> str:
    marked = re.compile(
        re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER) + r"\s*",
        flags=re.S,
    )
    if marked.search(text):
        return marked.sub(lambda _match: block + "\n", text, count=1)
    return re.sub(
        r"(?=\\section\{Conclusion\})",
        lambda _match: block + "\n",
        text,
        count=1,
    )


def main() -> int:
    files = tex_files()
    seen: set[str] = set()
    for path in files:
        label = paper_label(path)
        profile = PROFILES.get(label)
        if profile is None:
            raise RuntimeError(f"Missing profile for {label}: {path}")
        seen.add(label)
        title = paper_title(path, label)
        text = path.read_text()
        text = ensure_packages(text)
        text = replace_generic_abstract(text, title, profile)
        text = discipline_claims(text)
        text = normalize_data_availability(text)
        text = normalize_legacy_tables(text)
        text = insert_or_replace_upgrade(text, upgrade_block(label, title, profile))
        path.write_text(text)

    missing_files = sorted(set(PROFILES) - seen)
    if missing_files:
        raise RuntimeError(f"Profiles without manuscripts: {missing_files}")

    print(f"major universal upgrade applied to {len(files)} manuscripts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
