..
    contents:: Table of Contents
   :depth: 2
   :local:

.. _competitivedialogue_complaint_workflow:

Complaint Workflow
==================

For more detailed information read `Complaints <http://openprocurement.org/en/complaints.html>`_.

Tender Conditions Claims/Complaints
-----------------------------------

.. graphviz::

    digraph G {
        subgraph cluster_claim {
            label = "claim";
            claim; answered;
        }
        subgraph cluster_complaint {
            label = "complaint";
            pending; satisfied; accepted; stopping;
        }
        claim -> answered;
        satisfied -> resolved;
        edge[style=dashed];
        answered -> {pending,resolved};
        draft -> {claim,pending,mistaken};
        claim -> pending;
        {draft,claim,answered} -> cancelled;
        pending -> stopping;
        accepted -> stopping;
        edge[style=bold];
        accepted -> {declined,satisfied,stopped};
        pending -> {accepted,invalid};
        stopping -> {invalid,declined,satisfied};
        edge[label="auction" style=dotted];
        answered -> {declined,resolved,invalid};
    }

.. toctree::
    :maxdepth: 1

    complaints-tender

Tender Qualification Complaints
-------------------------------

.. graphviz::

    digraph G {
        subgraph cluster_complaint {
            label = "complaint";
            pending; accepted; stopping; satisfied;
        }
        satisfied -> resolved;
        edge[style=dashed];
        draft -> {pending,cancelled,mistaken};
        {pending,accepted} -> stopping;
        edge[style=bold];
        pending -> {accepted,invalid};
        stopping -> {invalid,declined,satisfied};
        accepted -> {declined,satisfied,stopped};
    }

.. toctree::
    :maxdepth: 1

    complaints-qualification

Tender Award Complaints
------------------------------

.. graphviz::

    digraph G {
        subgraph cluster_complaint {
            label = "complaint";
            pending; accepted; stopping; satisfied;
        }
        satisfied -> resolved;
        edge[style=dashed];
        draft -> {pending,cancelled,mistaken};
        {pending,accepted} -> stopping;
        edge[style=bold];
        pending -> {accepted,invalid};
        stopping -> {invalid,declined,satisfied};
        accepted -> {declined,satisfied,stopped};
    }

.. toctree::
    :maxdepth: 1

    complaints-award

Roles
-----

:Complainant:
    dashed

:Procuring entity:
    plain

:Reviewer:
    bold

:Chronograph:
    dotted

Statuses
--------

:draft:
    Initial status

    Complainant can submit claim, upload documents, cancel claim, and re-submit it.

:claim:
    Procuring entity can upload documents and answer to claim.

    Complainant can cancel claim.

:answered:
    Complainant can cancel claim, upload documents, accept solution or escalate claim to complaint.

:pending:
    Reviewer can upload documents and review complaint.

    Complainant can cancel claim.

:invalid:
    Terminal status

    Complaint recognized as invalid.

:declined:
    Terminal status

    Complaint recognized as declined.

:resolved:
    Terminal status

    Complaint recognized as resolved.

:cancelled:
    Terminal status

    Complaint cancelled by complainant.
